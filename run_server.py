from listeningthread import ListeningThread
from executorthread import ExecutorThread

def do_main_program(projects):
    global thread, stop
    thread = ListeningThread('localhost', 5000, ExecutorThread, projects=projects)
    thread.start()

def program_cleanup(signum, frame):
    global thread, stop
    thread.stop()
    stop = True

thread = None
stop = False

# Information
from project_reader import ProjectReader
reader = ProjectReader()
projects = {sc.get_project_label(): sc for sc in reader.get_project_classes()}
print('Available projects: %s' % list(projects.keys()))
print('')

# Execute
print("Executing...")
do_main_program(projects)
print("Done ! And now, listening...")

import signal
signal.signal(signal.SIGINT, program_cleanup)
signal.signal(signal.SIGTERM, program_cleanup)

# Wait
import time
while not stop:
    time.sleep(1)

from servicethread import ListeningThread
from executorthread import ExecutorThread

def do_main_program():
    global thread, stop
    thread = ListeningThread('localhost', 5000, ExecutorThread)
    thread.start()

def program_cleanup(signum, frame):
    global thread, stop
    thread.stop()
    stop = True

thread = None
stop = False

# Execute
print("Executing...")
do_main_program()
print("Done ! And now, listening...")

import signal
signal.signal(signal.SIGINT, program_cleanup)
signal.signal(signal.SIGTERM, program_cleanup)

# Wait
import time
while not stop:
    time.sleep(1)

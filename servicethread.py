import threading
from protocol import Protocol, ClosureException

class ServiceThread(threading.Thread):
    def run(self):
        self.execute()

    def execute(self):
        # Method where the service runs
        pass


class OneShotServiceThread(ServiceThread):
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        self.protocol = Protocol(clientsocket)

    def run(self):
        try:
            self.execute()
        except ClosureException:
            return
            
    def execute(self):
        # Method where the service runs
        pass


class PermanentServiceThread(ServiceThread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._is_running = True

    def is_running(self):
        return self._is_running

    def stop(self):
        self._is_running = False



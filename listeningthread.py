from servicethread import PermanentServiceThread
import socket

class ListeningThread(PermanentServiceThread):
    def __init__(self, host, port, threadclass, **kwargs):
        super().__init__()
        self.hostname = host
        self.port = port
        self.threadclass = threadclass
        self.kwargs = kwargs
    
    def execute(self):
        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_ATTACH_REUSEPORT_CBPF, 1)
        self.tcpsock.bind((self.hostname, self.port))
        self.tcpsock.listen(5)
        print('[port][%s] Listening' % self.port)
        
        while self.is_running():
            try:
                (clientsocket, (ip, port)) = self.tcpsock.accept()
                print('[port][{}] Accepted: {} <=> {}'.format(
                    self.port,
                    clientsocket.getsockname(),
                    clientsocket.getpeername(),
                ))
                newthread = self.threadclass(ip, port, clientsocket, **self.kwargs)
                newthread.start()
            except socket.timeout:
                pass

    def stop(self):
        super().stop()
        clientsocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocker.connect( (self.hostname, self.port) )
        self.tcpsock.close()
        print('[port][%s] Stop listening' % self.port)

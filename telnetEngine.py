import socket

class telnetEngine(object):
    def __init__(self,host,port):
        self.socket = None
        self.host = host
        self.port = port
    
    def connect(self):
        self.connection = socket.socket()
        self.connection.connect((self.host,self.port))


from telnetEngine import *
from parse import *

#AUTHOR: Pragun Goyal, 21, June, 2013
#This just opens a socket and looks for strings of the type
#null or <part name>

host = '127.0.0.1'
port = 9877

class displayClient(telnetEngine):
    def getFrame(self):
        frame_state = self.connection.recv(1000)
        return frame_state

displayClientObj = displayClient(host,port)


if __name__=="__main__":
    displayClientObj.connect()
    while(1):
        a = displayClientObj.getFrame()

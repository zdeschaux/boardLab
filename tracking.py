import socket, math
from parse import *

#AUTHOR: Pragun Goyal, 21, June, 2013
#This just opens a socket and looks for strings of the form
#<number of fiducials> <id> <x> <y> <angle> .... \n

host = '192.168.56.238'
port = 9876

pcb_id = '279'
selectTool_id = '283'

angle_bias = 180

xRes = 1920
yRes = 1080

def transform(a):
    res = {}
    res['x'] = xRes - a['x']
    res['y'] = yRes - a['y']
    res['angle'] = a['angle']
    return res


class tracking(object):
    def __init__(self):
        self.socket = None
        
    def connect(self):
        print "connecting.."
        self.connection = socket.socket()
        self.connection.connect((host,port))
        self.angle = 0

    def getFrame(self):
        frame_state = self.connection.recv(1000)
        #print frame_state
        frame_state = frame_state.strip()
        frame_dict = {}
        if frame_state != '':
            b = parse('{:d} {}',frame_state)
            if b is not None:
                frame_state = b[1]
                for i in range(b[0]):
                    oneFiducial = parse('{id:d} {x:d} {y:d} {angle:f}{rest}',frame_state)
                    res = transform(oneFiducial)
                    frame_dict[oneFiducial['id']] = {'x':res['x'],'y':res['y'],'angle':res['angle']}
                    frame_state =  oneFiducial['rest']
        print frame_dict
        return frame_dict


if __name__=="__main__":
    trackingObj = tracking()
    trackingObj.connect()
    while(1):
        a = trackingObj.getFrame()
        print a

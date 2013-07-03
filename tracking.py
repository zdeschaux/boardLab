import socket, math
from parse import *

#AUTHOR: Pragun Goyal, 21, June, 2013
#This just opens a socket and looks for strings of the form
#<number of fiducials> <id> <x> <y> <angle> .... \n

host = '192.168.56.238'
port = 1234

pointer_id = 0
pcb_id = 108

angle_bias = 180

class tracking(object):
    def __init__(self):
        self.socket = None
        
    def connect(self):
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
            frame_state = b[1]
            for i in range(b[0]):
                oneFiducial = parse('{id:d} {x:d} {y:d} {angle:f}{rest}',frame_state)
                frame_dict[oneFiducial['id']] = {'x':oneFiducial['x'],'y':oneFiducial['y'],'angle':oneFiducial['angle']}
                frame_state =  oneFiducial['rest']
                #print frame_state
             #print frame_dict
            print frame_dict

            if pcb_id in frame_dict:
                frame_dict[pcb_id]['angle'] *= (-1.0)
                frame_dict[pcb_id]['angle'] += angle_bias
                
            if pointer_id in frame_dict:
                pass

            return frame_dict


if __name__=="__main__":
    trackingObj = tracking()
    trackingObj.connect()
    while(1):
        a = trackingObj.getFrame()
        print a

import socket
from parse import *

#AUTHOR: Pragun Goyal, 21, June, 2013
#This just opens a socket and looks for strings of the form
#<number of fiducials> <id> <x> <y> <angle> .... \n

host = '192.168.56.1'
port = 1234


def connectTracker():
    s = socket.socket()
    s.connect((host,port))
    return s

def getTrackingFrame(connection):
    frame_state = connect.recv(200)
    frame_state = frame_state.strip()
    frame_dict = {}
    if frame_state != '':
        b = parse('{:d} {}',frame_state)
        frame_state = b[1]
        for i in range(b[0]):
            oneFiducial = parse('{id:d} {x:d} {y:d} {angle:f}{rest}',frame_state)
            #print 'oneFiducial',oneFiducial,i
            frame_dict[oneFiducial['id']] = {'x':oneFiducial['x'],'y':oneFiducial['y'],'angle':oneFiducial['angle']}
            frame_state =  oneFiducial['rest']
            #print frame_state
        #print frame_dict
    return frame_dict


if __name__=="__main__":
    connection = connectTracker()
    while(1):
        a = getTrackingFrame(connection)
        print a


        

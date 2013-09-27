# AUTHOR: Pragun Goyal, 26, September, 2013
# I talk to the Arduino connected to the buttons on the probe
# and generate events every time the user click, rubs, tickles or makes love to the probe 

# If the user makes love, then I generate huge number of events in excitement.

from config import probePort
import serial

class probe(object):
    def __init__(self,serialPort):
        self.serialPortName = serialPort
        self.serial = serial.Serial(serialPort,115200,timeout=1)

    def getEvents(self):
        evt = None
        a = self.serial.readline()
        if a.startswith('AP'):
            evt = {'button':'back','event':'press'}
        if a.startswith('AR'):
            evt = {'button':'back','event':'release'}
        if a.startswith('BP'):
            evt = {'button':'front','event':'press'}
        if a.startswith('BR'):
            evt = {'button':'front','event':'release'}
        return evt

probeObj = probe(probePort)

if __name__=="__main__":
    while(1):
        a = probeObj.getEvents()
        print a


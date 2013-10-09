# AUTHOR: Pragun Goyal, 21, June, 2013
# Modified: September, 3 2013. Removed all telnet crap used to talk to AR marker tracking softwares. This just talks to the polhemus now.

from config import probeTipOffset, fastrakPort
from polhemus import Fastrak
import sys

rawonly = False
if len(sys.argv) >= 2 and sys.argv[1] == 'rawonly':
    rawonly = True

class tracking(object):
    def __init__(self,serialPort):
        self.fastrak = Fastrak(logFile='rawlog.raw',serialPort=fastrakPort,fixedPoints=[probeTipOffset])
        self.fastrak.setup(reset=False)
        self.fastrak.setContinuous()

    def getFrame(self):
        a = self.fastrak.readData()
        return a

trackingObj = tracking(fastrakPort)

if __name__=="__main__":
    while(1):
        a = trackingObj.getFrame()
        if a is not None:
            if rawonly:
                m = ''
                for i in a[0]:
                    m += str(i)
                    m += ' '
                for i in a[1]:
                    m += str(i)
                    m += ' '
                print m
            else:
                print a


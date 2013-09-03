# AUTHOR: Pragun Goyal, 21, June, 2013
# Modified: September, 3 2013. Removed all telnet crap used to talk to AR marker tracking softwares. This just talks to the polhemus now.

from config import probeTipOffset, fastrakPort

class tracking(object):
    def __init__(self,serialPort):
        self.fastrak = Fastrak(logFile='rawlog.raw',serialPort='/dev/ttyUSB0',fixedPoints=[probeTipOffset])
        self.fastrak.setup(reset=True)
        self.fastrak.setContinuous()

    def getFrame(self):
        a = self.fastrak.readData()
        return a

trackingObj = tracking(fastrakPort)

if __name__=="__main__":
    trackingObj.connect()
    while(1):
        a = trackingObj.getFrame()
        print a


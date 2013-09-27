import serial, time

class Multimeter(object):
    def __init__(self,port='/dev/ttyUSB0'):
        ser = serial.Serial(port,9600,timeout=1,dsrdtr=True, stopbits=serial.STOPBITS_TWO)
        self.ser = ser
        self.id = None

    def writeCommand(self,cmd):
        wcmd = cmd + '\n'
        self.ser.write(wcmd)
        time.sleep(0.05)

    def getId(self):
        self.writeCommand('*IDN?')
        resp = self.ser.readline()
        self.id = resp
        return resp

    def reset(self):
        self.writeCommand('*RST')
        time.sleep(1)

    def clear(self):
        self.writeCommand('*CLS')

    def setSystem(self,cmd):
        wcmd = 'SYST:'+cmd
        self.writeCommand(wcmd)

    def getSystem(self):
        self.writeCommand('SYST?')
        resp = self.ser.readline()
        print resp

    def display(self,state):
        if state:
            self.writeCommand('DISPLAY 1')
        else:
            self.writeCommand('DISPLAY 0')


    def setupForRemote(self):
        a = self.ser.readline()
        self.getId()
        self.clear()
        self.reset()
        self.clear()
        self.display(True)
        self.setSystem('REM')
        self.clear()
        self.readError()
        
    def measure(self,what="VOLT:DC",range=10.0,resolution=0.003):
        wcmd = 'MEAS:'+what+"? %f,%f"%(range,resolution,)
        self.writeCommand(wcmd)
        resp = self.ser.readline()
        print 'resp',resp
        return float(resp)

    def readError(self):
        self.writeCommand('SYST:ERROR?')
        resp = self.ser.readline()
        print resp
        return resp
   
multimeterObj = Multimeter()
multimeterObj.setupForRemote()

     
if __name__ == "__main__":
    print multimeterObj.id
    while(True):
        voltage = multimeterObj.measure()
        print voltage


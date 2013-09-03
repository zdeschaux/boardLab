import serial, time


class Multimeter(object):
    def __init__(self,port='/dev/ttyUSB0'):
        ser = serial.Serial()
        ser.port = '/dev/ttyUSB0'
        ser.baudrate = 9600
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = 1
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.writeTimeout = 2
        self.ser = ser
        self.id = None

    def connect(self):
        self.ser.open()

    def writeCommand(self,cmd):
        wcmd = cmd + '\n'
        self.ser.write(wcmd)
        time.sleep(0.05)

    def getId(self):
        self.writeCommand('*IDN?')
        resp = self.ser.readline()
        self.id = resp
        #print resp
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
        self.connect()
        self.getId()
        self.clear()
        self.reset()
        self.clear()
        self.display(True)
        self.setSystem('REM')
        
        
    def measure(self,what="VOLT:DC",range=10.0,resolution=0.003):
        wcmd = 'MEAS:'+what+"? %f,%f"%(range,resolution,)
        self.writeCommand(wcmd)
        resp = self.ser.readline()
        return float(resp)

    def readError(self):
        a.writeCommand('SYST:ERROR?')
        resp = a.ser.readline()
        print resp
        return resp
        
if __name__ == "__main__":
    a = Multimeter()
    a.setupForRemote()
    print a.id
    voltage = a.measure()
    print voltage

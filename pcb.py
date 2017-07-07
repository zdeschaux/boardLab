# Pragun Maharaj, 
# Notes:
# flip() functions are deprecated, they were used when I didnt know how 
# to set cairo context up with a reflecting matrix

import inspect, parse, math, time, sys
import cairo
from cairoStuff import *
from config import *
from config import pcb_to_display_pixel_scale as scale, pcbLineThickness as lineThickness, viaRadius, consecutiveClickInterval, calibrationClickInterval
import json
import  xml.etree.ElementTree as ET
from numpy import *
from plane import Plane
from colors import *
import threading
        

def rotate(x,y,theta):
    rotMat = matrix(((math.cos(theta),math.sin(theta)),((-1)*math.sin(theta),math.cos(theta)),))
    inpVect = matrix(((x,),(y,),))
    outVect = rotMat * inpVect
    X = outVect[0,0]
    Y = outVect[1,0]
    return (X,Y)


class PCB(Screen):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__(self,fileName,usingMouse = False, multimeter=None, x=10.0, y=120.0,modeupdate=None):

        Screen.__init__( self )
        #PCB file loading stuff
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.elements = []
        self.multimeter = multimeter


        self.measurementId = 0
        self.signals = []
        self.loadElements()
        self.loadSignals()
        self.findMinRectangles()

        self.usingMouse = usingMouse #Very lame

        #Here we create a reflecting cairo matrix so that we dont have to flip the PCB 
        self.reflectingMatrix = cairo.Matrix(xx=1.0,yx=0.0,xy=0.0,yy=-1.0,x0=0.0,y0=1100.0)

        ## x,y is where I'm at
        self.x, self.y = (x,y)
        ## rx,ry is point of rotation
        self.rx, self.ry = -10, -25
        ## rot is angle counter
        self.rot = 0.0
        self.connect ( 'button-press-event' ,self.buttonPress)
        self.connect ( 'button-release-event' ,self.buttonRelease)
        self.lastButtonTimeStamp = None

        #We want to begin in calibration, unless the user is using the mouse only
        self.modeupdate = modeupdate
        self.mode = 'calibration'
        if self.usingMouse:
            self.mode = 'select'
        
        self.selectedSignalForCalibration = 0
        self.selectedViaForCalibration = 0
        self.calibrated = False

        self.triggerPressed = False

        self.tipProjectionX = 0.0
        self.tipProjectionY = 0.0

        self.mouseX = 0.0
        self.mouseY = 0.0

        #This is a hack to select conviniently spaced vias in the calibration routine        
        self.viaPairs = [(1,10),(1,15),(1,26)]
        self.selectNextViaForCalibration()
        

    def selectedVia(self):
        return self.signals[self.selectedSignalForCalibration].vias[self.selectedViaForCalibration]


    def modeRelease(self):
        if self.lastButtonTimeStamp is not None:
            timeStamp = time.time()
            diff = timeStamp - self.lastButtonTimeStamp
            self.lastButtonTimeStamp = None
            print 'Time between click and release',diff
            if diff <= consecutiveClickInterval:
                return  
            if diff > consecutiveClickInterval and diff < calibrationClickInterval:
                if self.mode == 'calibration':
                    self.selectNextViaForCalibration()
                    print 'moving on to the next calibration via:%d signal:%d'%(self.selectedViaForCalibration,self.selectedSignalForCalibration)
                else:
                    if self.mode == 'select':
                        self.mode = 'voltmeter'
                    elif self.mode == 'voltmeter':
                        self.mode = 'wave'
                    elif self.mode == 'wave':
                        self.mode = 'datasheet'
                    elif self.mode == 'datasheet':
                        self.mode = 'select'
                    else:
                        self.mode = 'select'

            if diff >= calibrationClickInterval:
                self.calibrationIntervalEvent()
                self.mode = 'calibration'

            if self.modeupdate is not None:
                self.modeupdate(self.mode)



    def triggerRelease(self):
        if self.mode == 'calibration':
            if self.selectedVia().calibrating:
                self.selectedVia().calibrating = False
        if self.mode == 'wave':
            self.triggerPressed = False
            self.measurementId += 1


    def buttonRelease(self,a,b):
        # Only mouse/trackpad release
        if b.button == 3:
            self.modeRelease()
        if b.button == 1:
            self.triggerRelease()
            
    def calibrationIntervalEvent(self):
        if self.mode == 'calibration':
            self.dumpCalibrationData()
            self.calibrate()
            self.mode = 'select'
        else:
            self.mode = 'calibration'
        self.lastButtonTimeStamp = None
        
        if self.modeupdate is not None:
            self.modeupdate(self.mode)
    

    def selectNextViaForCalibration(self):
        self.selectedVia().selected = False
        p = self.viaPairs.pop(0)
        (self.selectedSignalForCalibration,self.selectedViaForCalibration) = p
        self.viaPairs.append(p)
        self.selectedVia().selected = True


    def dumpCalibrationData(self):
        print 'Dumping calibration data into:%s' % (calibrationDataFile)
        f = open(calibrationDataFile,'w')
        viaList = []
        for i in self.signals:
            for j in i.vias:
                k = {'x':j.x,'y':j.y,'data':j.calibrationData}
                viaList.append(k)
        f.write(json.dumps(viaList))
        f.close()
        print 'Done dumping....'


    def probeEvent(self,b):
        #I process probeEvents and send them down some channel
        if b['button'] == 'front':
            if b['event'] == 'press':
                self.triggerPress()
            if b['event'] == 'release':
                self.triggerRelease()

        if b['button'] == 'back':
            if b['event'] == 'press':
                self.modePress()
            if b['event'] == 'release':
                self.modeRelease()


    def modePress(self):
        # I come here, from any event generation if it has been mapped to modePress
        self.lastButtonTimeStamp = time.time()


    def triggerPress(self):
        # I come here, from any event generation if it has been mapped to triggerPress
        if self.mode == 'calibration':
            self.selectedVia().calibrationData = []
            self.selectedVia().calibrating = True
            
        if self.mode == 'select' or self.mode == 'voltmeter' or self.mode == 'wave' or self.mode == 'datasheet':
            (x,y) = self.transformToPCBRef(self.tipProjectionX,self.tipProjectionY)
            if self.mode == 'select':
                for element in self.elements:
                    a = element.checkUnderMouse(x,y)
                    if a:
                        self.emit('ui_event',json.dumps({'type':'select','partName':element.partName}))

            if self.mode == 'datasheet':
                for element in self.elements:
                    a = element.checkUnderMouse(x,y)
                    if a:
                        self.emit('ui_event',json.dumps({'type':'datasheet','partName':element.partName}))

            if self.mode == 'voltmeter':
                for element in self.elements:
                    a = element.checkPadsAndSMDsUnderMouse(x,y)
                    if a is not None:
                        data = {}
                        data['positive'] = {'partName':element.partName,'pad':a}
                        #negative is connected to the ground of the circuit
                        data['type'] = 'VDC'
                        data['value'] = self.multimeter.measure()
                        self.emit('ui_event',json.dumps(data))

            if self.mode == 'wave':
                for element in self.elements:
                    a = element.checkPadsAndSMDsUnderMouse(x,y)
                    if a is not None:
                        data = {}
                        data['id'] = self.measurementId
                        data['positive'] = {'partName':element.partName,'pad':a}
                        #negative is connected to the ground of the circuit
                        data['type'] = 'VAC'
                        data['value'] = self.multimeter.measure2()
                        self.originalMeasurement = data
                        self.emit('ui_event',json.dumps(data))
                        self.triggerPressed = True
                        measurementThread = threading.Thread(target=self.takeMeasurements)
                        measurementThread.start()
                

    def takeMeasurements(self):
        while(self.triggerPressed):
            self.originalMeasurement['value'] = self.multimeter.measure2()
            print 'sending measurement'
            self.emit('ui_event',json.dumps(self.originalMeasurement))
            time.sleep(0.2)

    def buttonPress(self,a,b):
        # I come here, if a MOUSE button is pressed,
        # this should happen if someone's testing me using a mouse or a trackpad
        print 'Button pressed',b.button
        if b.button == 3:
            self.modePress()
        if b.button == 1:
            self.triggerPress()
                 
    def doTick(self):
        pass
    
    def draw(self, width, height):
        if self.lastButtonTimeStamp is not None:
            diff = time.time() - self.lastButtonTimeStamp
            if diff > calibrationClickInterval:
                self.calibrationIntervalEvent()

        #print "I also draw."
        ## A shortcut
        cr = self.cr
        cr.set_matrix(self.reflectingMatrix)
        cr.save()
        cr.scale(scale,scale)

        cr.set_line_width(lineThickness)
        
        if self.mode is not 'calibration':
            if self.usingMouse:
                (self.tipProjectionX,self.tipProjectionY) = cr.device_to_user(self.mouseX,self.mouseY)
                
            cr.set_source_rgb(*tipColor)
            cr.arc(self.tipProjectionX, self.tipProjectionY, viaRadius, -2*math.pi, 0)
            cr.stroke()

            if False: #Different pointers disabled
                if self.mode == 'select':
                    cr.arc(self.tipProjectionX, self.tipProjectionY, viaRadius, -2*math.pi, 0)
                    cr.stroke()
                    
                    if self.mode == 'voltmeter':
                        cr.arc(self.tipProjectionX, self.tipProjectionY, 3*viaRadius, -2*math.pi, 0)
                        cr.stroke()
                        cr.arc(self.tipProjectionX, self.tipProjectionY, viaRadius, -2*math.pi, 0)
                        cr.fill()

                    if self.mode == 'wave':
                        cr.arc(self.tipProjectionX, self.tipProjectionY, 3*viaRadius, -2*math.pi, 0)
                        cr.move_to(self.tipProjectionX-1.5*viaRadius, self.tipProjectionY)
                        cr.line_to(self.tipProjectionX+1.5*viaRadius, self.tipProjectionY)
                        cr.move_to(self.tipProjectionX, self.tipProjectionY-1.5*viaRadius)
                        cr.line_to(self.tipProjectionX, self.tipProjectionY+1.5*viaRadius)
                        cr.stroke()

                    if self.mode == 'datasheet':
                        cr.set_source_rgb(0.0,0.0,1.0)
                        cr.arc(self.tipProjectionX, self.tipProjectionY, viaRadius, -2*math.pi, 0)
                        cr.stroke()
                
        applyTranslation(cr,self.x,self.y)
        applyRotationAboutPoint(cr,0,0,self.rot)
        for element in self.elements:
            element.draw(cr)
        for signal in self.signals:
            signal.draw(cr)
        #Draw what mode we're in
        cr.restore()
     

    def transformToPCBRef(self,x,y):
        #x,y are in the global reference frame (the frame of reference of the display)
        #X,Y are in the reference frame of the pcb
        (x_p,y_p) = (x-self.x,y-self.y)
        theta = (1)*self.rot
        rotMat = matrix(((math.cos(theta),math.sin(theta)),((-1)*math.sin(theta),math.cos(theta)),))
        inpVect = matrix(((x_p,),(y_p,),))
        outVect = rotMat * inpVect
        X = outVect[0,0]
        Y = outVect[1,0]
        X = float(X)
        Y = float(Y)
        return (X,Y)


    def findMinRectangles(self):
        for i in self.elements:
            i.findMinRectangle()

    def getElementsWithTagName(self,tagName):
        returnArray = []
        for child in self.root.iter(tagName):
            returnArray.append(child)
        return returnArray
 
    def loadElements(self):
        a = self.getElementsWithTagName('element')
        for i in a:
            self.elements.append(BasicElement(i,self))
              
    def loadSignals(self):
        a = self.getElementsWithTagName('signal')
        for i in a:
            self.signals.append(SignalElement(i,self))

    def flip(self):
        for i in self.elements:
            i.flip()
        for i in self.signals:
            i.flip()

    def processMouseFrame(self,frame):
        (self.mouseX,self.mouseY) = (frame['x'],frame['y'])

    def processTrackingFrame(self,frame):
        if self.mode == 'calibration':
            if self.selectedVia().calibrating:
                self.selectedVia().calibrationData.append(frame)

        if self.calibrated:
            #calculate tip position for the UI
            tipTx = np.array(frame[2])
            tipTxProjection = self.plane.projectPoint(tipTx)
            tipPlane = self.plane.planeRepresentationForSensorPoint(tipTxProjection)
            tipPlaneCentroid = tipPlane - self.centroidB
            sTipPlaneCentroid = self.scaleAB*tipPlaneCentroid
            rsTipPlaneCentroid = np.dot(self.rotMat,sTipPlaneCentroid)
            rsTipPCB = rsTipPlaneCentroid + self.centroidA
            rsTipPCB.shape = (2,)
            self.tipProjectionX = rsTipPCB[0]+self.x
            self.tipProjectionY = rsTipPCB[1]+self.y            


    def calibrate(self):
        # Calibration comes in three phases
        # Phase 1, Find the plane of the PCB
        # make a list of all data points
        print 'Calibrating...'
        print 'Finding PCB plane..'
        dataPoints = []
        for i in self.signals:
            for j in i.vias:
                for k in j.calibrationData:
                    dataPoints.append(k[2])
        self.plane = Plane.leastSquaresFit(dataPoints)
        print self.plane
        self.plane.parameterize()
        #Now, we have the plane. We should find two axes on the plane
        self.findRotationScaleTranslation()
        self.calibrated = True

        
    def findRotationScaleTranslation(self):
        # I use the technique described in http://igl.ethz.ch/projects/ARAP/svd_rot.pdf
        # to calculate the rotation matrix
        # We begin by assembling both pointclouds
        pCloudA = []
        pCloudB = []
        for signal in self.signals:
            for via in signal.vias:
                for dataPoint in via.calibrationData:
                    tipPosition = dataPoint[2]
                    tipPositionOnPCBPlane = self.plane.planeRepresentationForSensorPoint(tipPosition)
                    pCloudA.append(np.array([via.x,via.y]))
                    pCloudB.append(np.array(tipPositionOnPCBPlane))

        f = open('pointcloud.dat','w')
        logCloudA = []
        logCloudB = []

        for i in range(len(pCloudA)):
            logCloudA.append([pCloudA[i][0],pCloudA[i][1]])
            logCloudB.append([pCloudB[i][0],pCloudB[i][1]])

        t = {'A':logCloudA,'B':logCloudB}
        f.write(json.dumps(t))
        f.write('\n')
        f.close()

        rotMat, centroidA, centroidB ,scaleAB = Plane.findRotationTranslationScaleForPointClouds(pCloudA,pCloudB)
        
        self.rotMat = rotMat
        self.centroidA = centroidA
        self.centroidB = centroidB
        self.scaleAB = scaleAB
        self.calibrated = True
        

class SignalElement(object):
    def __init__(self,element,pcb):
        self.element = element
        self.pcb = pcb
        self.name = element.attrib['name']
        self.sigClass = None
        self.vias = []
        if 'class' in element.attrib:
            self.sigClass = element.attrib['class']

        self.loadVias()

    def __repr__(self):
        return 'Signal Name:%s class:%s'%(self.name,self.sigClass)

    def loadVias(self):
       for child in self.element.iter('via'):
           self.vias.append(Via(child,self))

    def draw(self,cr):
        for via in self.vias:
            via.draw(cr)

    def flip(self):
        for i in self.vias:
            i.flip()



class Via(object):
    def __init__(self,element,signal):
        self.signal = signal
        self.element = element
        self.x = float(element.attrib['x'])
        self.y = float(element.attrib['y'])
        self.shape = element.attrib['shape']
        self.selected = False
        self.calibrating = False
        self.calibrationData = []

    def __repr__(self):
        return 'Via on Signal:%s at x:%f,y:%f shaped: %s'%(self.signal.name,self.x,self.y,self.shape)


    def color(self):
        if self.selected:
            if self.calibrating:
                return calibratingViaColor
            else:
                return selectedViaColor
        else:
            return viaColor

    def draw(self,cr):
        cr.save()
        if self.selected and self.signal.pcb.mode == 'calibration':
            cr.set_line_width(4*lineThickness)
        cr.set_source_rgb(*self.color())
        cr.arc(self.x, self.y, viaRadius, -2*math.pi, 0)
        cr.fill()
        cr.restore()


    def flip(self):
        self.y = 0.0-self.y



class BasicElement(object):
    def __init__(self,element,pcb):
        self.element = element
        self.underMouse = False
        self.pcb = pcb

        self.libraryName = element.attrib['library']
        self.partName = element.attrib['name']
        self.packageName = element.attrib['package']
        print element,element.tag,element.attrib
        self.x = float(element.attrib['x'])
        self.y = float(element.attrib['y'])
        self.rot = 0
        self.pads = []
        self.smds = []

        if 'rot' in element.attrib:
            rot = element.attrib['rot']
            print rot
            rotParse = parse.parse('R{:d}',rot)
            if rotParse is None:
                rotParse = parse.parse('MR{:d}',rot)
            self.rot = float(rotParse[0])*(math.pi/180)
            print self.rot

        self.drawingElements = []

        self.findFromLibrary()
        self.loadFromLibrary()
        self.loadPads()
        self.loadSMDs()

    def __repr__(self):
        return ','.join([self.partName, self.packageName, self.libraryName])
        
    def findFromLibrary(self):
        #First find the library
        library = None
        footPrint = None
        for i in self.pcb.root.iter('library'):
            if i.attrib['name'] == self.libraryName:
                library = i
                break
        #Second find the part 
        for i in library.iter('package'):
            if i.attrib['name'] == self.packageName:
                footPrint = i
                break
        self.library = library
        self.footPrint = footPrint

    def loadPads(self):
        for i in self.footPrint.findall('pad'):
            self.pads.append(Pad(i,self))

    def loadSMDs(self):
        for i in self.footPrint.findall('smd'):
            self.pads.append(SMD(i,self))

    def loadFromLibrary(self):
        for i in self.footPrint:
            if i.tag == 'wire' and i.attrib['layer'] == '21':
                self.drawingElements.append(Wire(i,self))
                
    #rewrite
    def fontPosition(self):
        a = self.relativePosition()
        return (a[0],a[1])

    def checkUnderMouse(self,x,y):
        (absMinX,absMinY) = self.absoluteCoordinates(self.minX,self.minY)
        (absMaxX,absMaxY) = self.absoluteCoordinates(self.maxX,self.maxY)
        if absMinX <= x and absMaxX >= x and absMinY <= y and absMaxY >= y:
            self.underMouse = True
            return True
        else:
            self.underMouse = False
            return False

    def checkPadsAndSMDsUnderMouse(self,x,y):
        for i in self.pads:
            a = i.checkUnderMouse(x,y)
            if a:
                return i.name
        for i in self.smds:
            a = i.checkUnderMouse(x,y)
            if a:
                return i.name
    
    def color(self):
        if self.underMouse:
            return red
        else:
            return green

    def draw(self,cr):
        cr.save()
        for item in self.drawingElements:
            item.draw(cr)
        self.drawMinRectangle(cr)
        for pad in self.pads:
            pad.draw(cr)
        for smd in self.smds:
            smd.draw(cr)
        cr.restore()

    def flip(self):
        self.y = 0.0 - self.y
        for i in self.drawingElements:
            i.flip()

    def findMinRectangle(self):
        maxX = float('-inf')
        minX = float('inf')
        minY = float('inf')
        maxY = float('-inf')
        for i in self.drawingElements:
            if type(i) == Wire:
                (x1,y1,x2,y2) = (i.x1,i.y1,i.x2,i.y2)
                maxX = max(maxX,x1,x2)
                minX = min(minX,x1,x2)
                minY = min(minY,y1,y2)
                maxY = max(maxY,y1,y2)
        self.maxX = maxX
        self.minX = minX
        self.minY = minY
        self.maxY = maxY
        self.rectLengthX = abs(self.maxX-self.minX)
        self.rectLengthY = abs(self.maxY-self.minY)

    def drawMinRectangle(self,cr):
        if self.underMouse:
            cr.set_source_rgb(*minRectangleSelected)
        else:
            cr.set_source_rgb(*minRectangle)
        (absMinX,absMinY) = self.absoluteCoordinates(self.minX,self.minY)
        cr.rectangle(absMinX, absMinY, self.rectLengthX, self.rectLengthY )
        cr.stroke()

    def absoluteCoordinates(self,x,y):
        x1 = self.x + x
        y1 = self.y + y
        return (x1,y1)


class Pad(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        self.x = -float(item.attrib['x'])
        self.y = float(item.attrib['y'])
        (self.x,self.y) = rotate(self.x,self.y,-self.parent.rot)

        self.underMouse = False
        self.name = item.attrib['name']
        if 'diameter' in item.attrib.keys():
            self.radius = float(item.attrib['diameter'])/2
        if 'shape' in item.attrib.keys():
            self.shape = item.attrib['shape']
    
    def absoluteCoordinates(self):
        (x,y) = self.parent.absoluteCoordinates(self.x,self.y)
        return (x,y)
    
    def color(self):
        if self.underMouse:
            return padSelected
        else:
            return pad

    def draw(self,cr):
        if hasattr(self,'radius'):
            cr.set_source_rgb(*self.color())
            (x,y) = self.absoluteCoordinates()
            cr.arc(x,y,self.radius,0,2*math.pi)
            cr.stroke()

            cr.set_source_rgb(0.5,0.5,0.5)
            (x,y) = self.absoluteCoordinates()
            cr.arc(x,y,1.8*self.radius,0,2*math.pi)
            cr.stroke()

    def checkUnderMouse(self,x,y):
        if hasattr(self,'radius'):
            (x1,y1) = self.absoluteCoordinates()
            distance = math.sqrt(((x-x1)*(x-x1))+((y-y1)*(y-y1)))
            if distance < 1.8*self.radius:
                self.underMouse = True
            else:
                self.underMouse = False
            return self.underMouse

class SMD(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        self.x = float(item.attrib['x'])
        self.y = float(item.attrib['y'])
        self.name = item.attrib['name']
        self.rot = 0.0
        if 'rot' in item.attrib.keys():
            rot = item.attrib['rot']
            print rot
            rotParse = parse.parse('R{:d}',rot)
            if rotParse is None:
                rotParse = parse.parse('MR{:d}',rot)
            self.rot = float(rotParse[0])*(math.pi/180)

        rot =  - self.parent.rot
        rot2 = -self.rot - self.parent.rot
        self.underMouse = False

        (self.x,self.y) = rotate(self.x,self.y,rot)

        self.dx = float(item.attrib['dx'])
        self.dy = float(item.attrib['dy'])
        (self.dx,self.dy) = rotate(self.dx,self.dy,rot2)
        (self.dx,self.dy) = (self.dx,self.dy)
        (self.x,self.y) = (self.x-self.dx/2,self.y-self.dy/2)

    def color(self):
        if self.underMouse:
            return padSelected
        else:
            return pad

    def draw(self,cr):
        cr.set_source_rgb(*self.color())
        (x,y) = self.parent.absoluteCoordinates(self.x,self.y)
        cr.rectangle(x,y,self.dx,self.dy)
        cr.stroke()

    def checkUnderMouse(self,x,y):
        (x1,y1) = self.parent.absoluteCoordinates(self.x,self.y)
        (x2,y2) = self.parent.absoluteCoordinates(self.x+self.dx,self.y+self.dy)
        xMin = min(x1,x2)
        xMax = max(x1,x2)
        yMin = min(y1,y2)
        yMax = max(y1,y2)

        if x <= xMax and x >= xMin and y <= yMax and y >= yMin:
            self.underMouse = True
        else:
            self.underMouse = False
        return self.underMouse


class Wire(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        
        x1 = float(item.attrib['x1'])
        y1 = float(item.attrib['y1'])
        x2 = float(item.attrib['x2'])
        y2 = float(item.attrib['y2'])

        (X1,Y1) = rotate(x1,y1,(-1)*self.parent.rot)
        (X2,Y2) = rotate(x2,y2,(-1)*self.parent.rot)
        
        self.x1 = X1
        self.y1 = Y1
        self.x2 = X2
        self.y2 = Y2

    def absoluteCoordinates(self):
        (x1,y1) = self.parent.absoluteCoordinates(self.x1,self.y1)
        (x2,y2) = self.parent.absoluteCoordinates(self.x2,self.y2)
        return (x1,y1,x2,y2)
        
    def draw(self,cr):
        (x1,y1,x2,y2) = self.absoluteCoordinates()
        x1 = x1
        y1 = y1
        x2 = x2
        y2 = y2

        cr.set_source_rgb(*wire)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

    def flip(self):
        self.y1 = -self.y1
        self.y2 = -self.y2
        pass

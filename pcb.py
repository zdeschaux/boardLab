import inspect, parse, math
from cairoStuff import *
from config import *
from config import pcb_to_display_pixel_scale as scale
import  xml.etree.ElementTree as ET
from numpy import *

def rotate(x,y,theta):
    rotMat = matrix(((math.cos(theta),math.sin(theta)),((-1)*math.sin(theta),math.cos(theta)),))
    inpVect = matrix(((x,),(y,),))
    outVect = rotMat * inpVect
    X = outVect[0,0]
    Y = outVect[1,0]
    return (X,Y)

       
class SelectTool(object):
    def __init__(self):
        self.activated = False
        self.x = 0
        self.y = 0
    
    def draw(self,cr):
        if self.activated:
            cr.set_source_rgb(0.0,0.0,1.0)
            cr.rectangle(self.x, self.y, 10,10)
            cr.stroke()



class PCB(Screen):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__(self,fileName,displayCallback):
        Screen.__init__( self )
        #PCB file loading stuff
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.elements = []
        self.loadElements()
        self.findFiducial()
        self.flip()
        self.findMinRectangles()

        ## x,y is where I'm at
        self.x, self.y = 100, 100
        ## rx,ry is point of rotation
        self.rx, self.ry = -10, -25
        ## rot is angle counter
        self.rotBias = -(math.pi/2)
        self.rot = 0.0
        ## sx,sy is to mess with scale
        self.sx, self.sy = 0.5, 0.5
        self.setPositionScale(100,100,0.1)
        print self.findFiducial()
        self.connect ( 'motion-notify-event', self.mouseMotion)
        self.selectTool = SelectTool() 
        self.displayCallback = displayCallback
        
    def doTick(self):
        pass
    
    def mouseMotion(self,a,b):
        a = self.findModuleUnderMouse(b.x,b.y)
        print a
        if a is not None:
            self.displayCallback(a.partName)

    def draw(self, width, height):
        #print "I also draw."
        ## A shortcut
        cr = self.cr
        cr.save()
        applyTranslation(cr,self.x,self.y)
        applyRotationAboutPoint(cr,0,0,self.rot)
        for element in self.elements:
            element.draw(cr)
        cr.restore()
        self.selectTool.draw(cr)

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
        X = float(X)/scale
        Y = float(Y)/scale
        print (x,y),(X,Y)
        return (X,Y)

    def setPositionScale(self,x,y,rot):
        self.x = x
        self.y = y
        self.rot = rot
    
    def findModuleUnderMouse(self,x,y):
        (X,Y) = self.transformToPCBRef(x,y)
        for element in self.elements:
            #a = element.checkUnderMouse(X,Y)
            a = False
            element.checkPadsAndSMDsUnderMouse(X,Y)
            if a:
                return element
        return None
 
    def findFiducial(self):
        #first find the fiducial element
        for i in self.elements:
            if i.packageName.startswith('TOPCODE'):
                self.fiducial = i
                break

        fid_x = self.fiducial.x
        fid_y = self.fiducial.y
        #now bring everything in the document to the reference frameo of the fiducial
        for i in self.elements:
            i.x = i.x - fid_x
            i.y = i.y - fid_y

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
              
    def flip(self):
        for i in self.elements:
            i.flip()


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
            i.checkUnderMouse(x,y)
        for i in self.smds:
            i.checkUnderMouse(x,y)
    
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
            cr.set_source_rgb(1,0,0)
        else:
            cr.set_source_rgb(0,1,0)
        (absMinX,absMinY) = self.absoluteCoordinates(self.minX,self.minY)
        cr.rectangle(absMinX*scale, absMinY*scale, self.rectLengthX*scale, self.rectLengthY*scale )
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
            return (0.0,0.0,0.9)
        else:
            return (0.0,0.0,0.4)

    def draw(self,cr):
        if hasattr(self,'radius'):
            cr.set_source_rgb(*self.color())
            (x,y) = self.absoluteCoordinates()
            cr.arc(x*scale,y*scale,self.radius*scale,0,2*math.pi)
            cr.stroke()

    def checkUnderMouse(self,x,y):
        if hasattr(self,'radius'):
            (x1,y1) = self.absoluteCoordinates()
            distance = math.sqrt(((x-x1)*(x-x1))+((y-y1)*(y-y1)))
            if distance < self.radius:
                print self.name, self.parent.partName
                self.underMouse = True
            else:
                self.underMouse = False


class SMD(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        self.x = float(item.attrib['x'])
        self.y = float(item.attrib['y'])
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

        self.name = item.attrib['name']

    def color(self):
        if self.underMouse:
            return (0.0,0.0,0.9)
        else:
            return (0.0,0.0,0.4)

    def draw(self,cr):
        cr.set_source_rgb(*self.color())
        (x,y) = self.parent.absoluteCoordinates(self.x,self.y)
        cr.rectangle(x*scale,y*scale,self.dx*scale,self.dy*scale)
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
            print self.name, self.parent.partName
        else:
            self.underMouse = False


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
        x1 = x1*scale
        y1 = y1*scale
        x2 = x2*scale
        y2 = y2*scale

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

    def flip(self):
        self.y1 = -self.y1
        self.y2 = -self.y2
        pass

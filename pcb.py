import inspect, parse, math
from cairoStuff import *
from config import *
from config import pcb_to_display_pixel_scale as scale
import  xml.etree.ElementTree as ET
from numpy import *
import tracking

def getOWH(a):
    origin = a.GetOrigin()
    end = a.GetEnd()
    width = a.GetWidth()
    height = a.GetHeight()
    return (origin,width,height)

def printMembers(a):
    b = inspect.getmembers(a)
    for i in b:
        print i



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
    def __init__(self,fileName,tracker):
        Screen.__init__( self )
        #PCB file loading stuff
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.elements = []
        self.loadElements()
        self.findFiducial()
        self.flip()
        self.findMinRectangles()

        self.tracker = tracker
        ## x,y is where I'm at
        self.x, self.y = 100, 100
        ## rx,ry is point of rotation
        self.rx, self.ry = -10, -25
        ## rot is angle counter
        self.rot = 0.0
        ## sx,sy is to mess with scale
        self.sx, self.sy = 0.5, 0.5
        self.setPositionScale(100,100,0.1)
        print self.findFiducial()
        self.connect ( 'motion-notify-event', self.mouseMotion)
        self.selectTool = SelectTool() 
        
    def doTick(self):
        pass
                
    def mouseMotion(self,a,b):
        self.findModuleUnderMouse(b.x,b.y)

    def draw(self, width, height):
        if not noTrackingDebug:
            a = self.tracker.getFrame()
            if a != {}:
                if tracking.pcb_id in a:
                    self.x = a[tracking.pcb_id]['x']
                    self.y = a[tracking.pcb_id]['y']
                    self.rot = a[tracking.pcb_id]['angle']
                else:
                    self.x = 00
                    self.y = 00
                    selx.rot = 00
                        
                if tracking.selectTool_id in a:
                    self.selectTool.activated = True
                    self.selectTool.x = a[tracking.selectTool_id]['x']
                    self.selectTool.y = a[tracking.selectTool_id]['y']
                else:
                    self.selectTool.activated = False
        else:
            self.x = 00
            self.y = 00
            self.rot = 0
                            
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
            a = element.checkUnderMouse(X,Y)
 
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


    def loadFromLibrary(self):
        for i in self.footPrint:
            if i.tag == 'wire' and i.attrib['layer'] == '21':
                self.drawingElements.append(Wire(i,self))
                
    #rewrite
    def fontPosition(self):
        a = self.relativePosition()
        return (a[0],a[1])


    def checkUnderMouse(self,x,y):
        if self.minX <= x and self.maxX >= x and self.minY <= y and self.maxY >= y:
            self.underMouse = True
            return True
        else:
            self.underMouse = False
            return False
    
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

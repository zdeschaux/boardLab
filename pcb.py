import inspect
from cairoStuff import *
from config import *
from config import pcb_to_display_pixel_scale as scale
import  xml.etree.ElementTree as ET
import parse
import math
from numpy import *


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


class PCB(Screen):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__(self,fileName):
        Screen.__init__( self )
        #PCB file loading stuff
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.elements = []
        self.loadElements()

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

    def mouseMotion(self,a,b):
        self.findModuleUnderMouse(b.x,b.y)

    def draw( self, width, height ):
        ## A shortcut
        cr = self.cr
        cr.save()
        
        applyTranslation(cr,self.x,self.y)
        applyRotationAboutPoint(cr,0,0,self.rot)
       
        for element in self.elements:
            element.draw(cr)

        cr.restore()
        #self.rot += 0.1
        #print 'here I redrawed myself.'
    
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
        #self.scale = scale
    
    def findModuleUnderMouse(self,x,y):
        (X,Y) = self.transformToPCBRef(x,y)
        for element in self.elements:
            a = element.checkUnderMouse(X,Y)
 
    def findFiducial(self):
        pass

    def getElementsWithTagName(self,tagName):
        returnArray = []
        for child in self.root.iter(tagName):
            returnArray.append(child)
        return returnArray
 
    def loadElements(self):
        a = self.getElementsWithTagName('element')
        for i in a:
            self.elements.append(BasicElement(i,self))
        
    def loadPackages(self):
        a = self.getElementsWithTagName('package')
        self.packages = [BasicElement(b,self) for b in a]

    
            
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
        self.findMinRectangle()

        
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


    #rewrite
    def checkUnderMouse(self,x,y):
        if self.minX <= x and self.maxX >= x and self.minY <= y and self.maxY >= y:
            self.underMouse = True
            return True
        else:
            self.underMouse = False
            return False
    
    #rewrite
    def color(self):
        if self.underMouse:
            return red
        else:
            return green

    #rewrite
    def draw(self,cr):
        cr.save()
        applyRotationAboutPoint(cr,self.x*scale,self.y*scale,self.rot)
        for item in self.drawingElements:
            item.draw(cr)
        self.drawMinRectangle(cr)
        cr.restore()


    def findMinRectangle(self):
        maxX = float('-inf')
        minX = float('inf')
        minY = float('inf')
        maxY = float('-inf')

        for i in self.drawingElements:
            if type(i) == Wire:
                (x1,y1,x2,y2) = i.absoluteCoordinates()
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
        cr.rectangle(self.minX*scale, self.minY*scale, self.rectLengthX*scale, self.rectLengthY*scale )
        cr.stroke()

        
        
class Wire(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        self.x1 = float(item.attrib['x1'])
        self.y1 = float(item.attrib['y1'])
        self.x2 = float(item.attrib['x2'])
        self.y2 = float(item.attrib['y2'])

    def absoluteCoordinates(self):
        x1 = self.x1 + self.parent.x
        x2 = self.x2 + self.parent.x
        y1 = self.y1 + self.parent.y
        y2 = self.y2 + self.parent.y
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

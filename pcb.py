import inspect
from cairoStuff import *
from config import *
import  xml.etree.ElementTree as ET

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
        #self.loadPackages()
        self.loadElements()

        ## x,y is where I'm at
        self.x, self.y = 100, 100
        ## rx,ry is point of rotation
        self.rx, self.ry = -10, -25
        ## rot is angle counter
        self.rot = 0
        ## sx,sy is to mess with scale
        self.sx, self.sy = 0.5, 0.5
        
        self.setPositionScale(-700,-120,0)
        print self.findFiducial()


    def draw( self, width, height ):
        ## A shortcut
        cr = self.cr
        cr.save()
        
        applyTranslation(cr,100,100)
        applyRotationAboutPoint(cr,0,0,self.rot)
       
        for element in self.elements:
            element.draw(cr)

        cr.restore()
        #self.rot += 0.1
        #print 'here I redrawed myself.'
     
    def setPositionScale(self,x,y,rot):
        self.x = x
        self.y = y
        self.rot = rot
        #self.scale = scale
    
    def findModuleUnderMouse(self,x,y):
        for element in self.elements:
            a = element.checkUnderMouse(x,y)
 
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


    #rewrite
    def checkUnderMouse(self,x,y):
        sserRect = self.relativePosition()
        left = sserRect[0]
        top = sserRect[1]
        right = left + sserRect[2]
        bottom = top + sserRect[3]
        if left <= x and right >= x and top <= y and bottom >= y:
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
        for item in self.drawingElements:
            item.draw(cr)
        if False:
            relativeCoordinates = self.relativePosition()
            (startX,startY,width,height) = relativeCoordinates
            cr.set_line_join(cairo.LINE_JOIN_BEVEL)
            cr.rectangle(startX,startY, width, height)
            cr.set_source_rgb(0,0,0)
            cr.stroke()
            

                
class Wire(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        self.x1 = float(item.attrib['x1'])
        self.y1 = float(item.attrib['y1'])
        self.x2 = float(item.attrib['x2'])
        self.y2 = float(item.attrib['y2'])

    def draw(self,cr):
        x1 = self.x1 + self.parent.x
        x2 = self.x2 + self.parent.x
        y1 = self.y1 + self.parent.y
        y2 = self.y2 + self.parent.y

        x1 = x1*10
        y1 = y1*10
        x2 = x2*10
        y2 = y2*10

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()
        
        

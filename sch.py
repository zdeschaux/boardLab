import inspect, parse, math
from cairoStuff import *
from config import *
from config import sch_to_display_pixel_scale as scale
import  xml.etree.ElementTree as ET
from numpy import *
import sys


pinLengths = {
    'point':3,
    'short':5,
    'middle':7,
    'long':9,
}

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


class XMLElement(object):
    def getElementsWithTagName(self,tagName):
        returnArray = []
        for child in self.root.iter(tagName):
            returnArray.append(child)
        return returnArray


    def findRot(self):
        element = self.root
        rot = 0.0
        if 'rot' in element.attrib:
            rot = element.attrib['rot']
            rotParse = parse.parse('R{:d}',rot)
            if rotParse is None:
                rotParse = parse.parse('MR{:d}',rot)
            rot = float(rotParse[0])*(math.pi/180)
        return rot


class SCH(Screen,XMLElement):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__(self,fileName,displayCallback):
        Screen.__init__( self )
        #SCH file loading stuff
        self.x = 0
        self.y = 0
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.sheets = []
        self.loadSheets()
        self.selectedInstances = None
        
    def draw(self, width, height):
        '''
        Translates the canvas to x,y
        which in turn is set to the center of the selected component
        '''
        #print "I also draw."
        ## A shortcut
        applyTranslation(self.cr,self.x,self.y)
        self.sheets[0].draw(self.cr)

    def processFrame(self,frame):
        '''
        This takes in a display frame and selects all instances with the same part name
        '''
        frame = frame.strip()
        if not frame == 'null':
            if frame in self.sheets[0].instanceHash:
                self.selectInstance(self.sheets[0].instanceHash[frame])

    def loadSheets(self):
        '''
        Loads the sheets, but only the first sheet is used right now.
        '''
        a = self.getElementsWithTagName('sheet')
        for i in a:
            self.sheets.append(Sheet(i,self,self))
              
    def selectInstance(self,a):
        '''
        This selects all instances that come in the list a
        and centers the frame about the first one in the list.
        '''
        #Handle logistical stuff that has to happen to select an instance
        if self.selectedInstances is not None:
            for i in self.selectedInstances:
                i.selected = False
        self.selectedInstances = a
        for i in a:
            i.selected = True
        
        #Move x,y so that the first instance of the selected instances is at the center of the screen
        self.x = (width/2)-(a[0].x*scale)
        self.y = (height/2)-(a[0].y*scale)



class Sheet(XMLElement):
    def __init__(self,tag,parent,rootParent):
        self.root = tag
        self.parent = parent
        self.instances = []
        self.instanceHash = {}
        self.nets = []
        self.rootParent = rootParent
        
        self.loadInstances()
        print self.instanceHash
        self.loadNets()

    def loadInstances(self):
        a = self.getElementsWithTagName('instance')
        for i in a:
            p = Instance(i,self,self.rootParent)
            self.instances.append(p)
            if p.name not in self.instanceHash:
                self.instanceHash[p.name] = []
            self.instanceHash[p.name].append(p)

    def loadNets(self):
        a = self.getElementsWithTagName('net')
        for i in a:
            self.nets.append(Net(i,self,self.rootParent))

    def draw(self,cr):
        for i in self.instances:
            i.draw(cr)
        for i in self.nets:
            i.draw(cr)


class Net(XMLElement):
    def __init__(self,tag,parent,rootParent):
        self.root = tag
        self.parent = parent
        self.rootParent = rootParent
        self.segments = []
        
        self.loadSegments()

    def loadSegments(self):
        a = self.getElementsWithTagName('segment')
        for i in a:
            self.segments.append(Segment(i,self,self.rootParent))

    def draw(self,cr):
        cr.save()
        for i in self.segments:
            cr.set_source_rgb(0.0,0.0,0.4)
            i.draw(cr)
        cr.restore()


class Segment(XMLElement):
    def __init__(self,tag,parent,rootParent):
        self.root = tag
        self.parent = parent
        self.rootParent = rootParent
        self.wires = []
        
        self.loadWires()

    def loadWires(self):
        a = self.getElementsWithTagName('wire')
        for i in a:
            self.wires.append(Wire(i,self))

    def draw(self,cr):
        for i in self.wires:
            i.draw(cr)


class Instance(XMLElement):
    def __init__(self,tag,parent,rootParent):
        self.root = tag
        self.parent = parent
        self.rootParent = rootParent

        self.partName = self.root.attrib['part']
        self.x = float(self.root.attrib['x'])
        self.y = float(self.root.attrib['y'])
        self.gateName = self.root.attrib['gate']
        self.name = self.partName
        
        self.selected = False
        self.rot = self.findRot()
        self.gate = None
        self.devicesetElement = None
        self.deviceElement = None
        self.libraryElement = None
        self.libraryName = None
        self.deviceName = None
        self.devicesetName = None
        self.dataSheetFileName = None

        self.loadPart()
        self.loadDeviceset()
        self.loadGate()

    def color(self):
        if self.selected:
            return (0.7,0.0,0.0)
        else:
            return (0.3,0.0,0.0)
       
    def __repr__(self):
        a = 'Instance: %s from library %s deviceset %s @ (%f,%f,%f)'%(self.partName,self.libraryName,self.devicesetName,self.x,self.y,self.rot)
        return a

    def loadPart(self):
        a = self.rootParent.getElementsWithTagName('part')
        for i in a:
            if i.attrib['name'] == self.partName:
                self.libraryName = i.attrib['library']
                self.deviceName = i.attrib['device']
                self.devicesetName = i.attrib['deviceset']
                self.value = None
                if 'value' in i.attrib:
                    self.value = i.attrib['value']
            for j in i:
                if j.tag == 'attribute' and j.attrib['name'] == 'DATASHEET':
                    self.dataSheetFileName = j.attrib['value']
    
    def loadDeviceset(self):
        a = self.rootParent.getElementsWithTagName('library')
        for i in a:
            if i.attrib['name'] == self.libraryName:
                self.libraryElement = i
                for j in i.findall('devicesets/deviceset'):
                    if self.devicesetName == j.attrib['name']:
                        self.devicesetElement = j
                
    def loadGate(self):
        #Then load the gates themselves
        gateElements = self.devicesetElement.findall('gates/gate')
        for i in gateElements:
            if i.attrib['name'] == self.gateName:
                self.gate = Gate(i,self,self.rootParent)
                
    def draw(self,cr):
        cr.save()
        (tx,ty) = (self.x*scale,self.y*scale)
        applyTranslation(cr,tx,ty)
        applyRotationAboutPoint(cr,0,0,self.rot)
        cr.set_source_rgb(*self.color())
        self.gate.draw(cr)
        cr.restore()



class Gate(XMLElement):
    def __init__(self,element,parent,rootParent):
        self.root = element
        self.x = float(element.attrib['x'])
        self.y = float(element.attrib['y'])
        self.symbolName = element.attrib['symbol']
        self.parent = parent
        self.rootParent = rootParent
        self.libraryName = self.parent.libraryName
        self.libraryElement = self.parent.libraryElement
        self.symbol = None        
        self.loadSymbol()

    def loadSymbol(self):
        a = self.libraryElement.findall('symbols/symbol')
        for i in a:
            if i.attrib['name'] == self.symbolName:
                self.symbol = Symbol(i,self,self.rootParent)

    def draw(self,cr):
        self.symbol.draw(cr)



class TextLabel(XMLElement):
    def __init__(self,element,text,parent):
        self.root = element
        self.x = float(element.attrib['x'])
        self.y = float(element.attrib['y'])
        self.text = text

    def draw(self,cr):
        cr.save()
        cr.set_source_rgb(0.2,0.2,0.2)
        cr.select_font_face('Helvetica',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
        cr.move_to(self.x,self.y)
        cr.show_text(self.text)
        cr.restore()


class Symbol(XMLElement):
    def __init__(self,element,parent,rootParent):
        self.name = element.attrib['name']
        self.root = element
        self.parent = parent
        self.rootParent = rootParent
        self.libraryName = self.parent.libraryName
        self.libraryElement = self.parent.libraryElement
        self.wires = []
        self.rectangles = []
        self.pins = []
        self.textLabels = []
        
        self.loadRectangles()
        self.loadWires()
        self.loadPins()
        self.loadTextLabels()

    def loadWires(self):
        a = self.root.findall('wire')
        for i in a:
            self.wires.append(Wire(i,self))

    def loadRectangles(self):
        a = self.root.findall('rectangle')
        for i in a:
            self.rectangles.append(Rectangle(i,self))

    def loadPins(self):
        a = self.root.findall('pin')
        for i in a:
            self.pins.append(Pin(i,self))

    def loadTextLabels(self):
        a = self.root.findall('text')
        instance = self.parent.parent
        for i in a:
            if i.text == '>VALUE' and hasattr(instance,'value') and instance.value is not None:
                self.textLabels.append(TextLabel(i,instance.value,self))
            if i.text == '>NAME' and instance.name is not None:
                self.textLabels.append(TextLabel(i,instance.name,self))

            
    def __repr__(self):
        a = 'Symbol %s from library %s with %d wires'%(self.name,self.libraryName,len(self.wires))
        return a

    def draw(self,cr):
        for i in self.wires:
            i.draw(cr)
        for i in self.rectangles:
            i.draw(cr)
        for i in self.pins:
            i.draw(cr)
        for i in self.textLabels:
            i.draw(cr)

        
class Wire(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        
        x1 = float(item.attrib['x1'])
        y1 = float(item.attrib['y1'])
        x2 = float(item.attrib['x2'])
        y2 = float(item.attrib['y2'])

        rot = 0.0
        if hasattr(self.parent,'rot'):
            rot = self.parent.rot
        (X1,Y1) = rotate(x1,y1,(-1)*rot)
        (X2,Y2) = rotate(x2,y2,(-1)*rot)
        
        self.x1 = X1
        self.y1 = Y1
        self.x2 = X2
        self.y2 = Y2
        
    def draw(self,cr):
        x1 = self.x1*scale
        y1 = self.y1*scale
        x2 = self.x2*scale
        y2 = self.y2*scale

        #cr.set_source_rgb(0, 0, 0)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

    def flip(self):
        self.y1 = -self.y1
        self.y2 = -self.y2
        pass


class Pin(XMLElement):
    def __init__(self,root,parent):
        self.root = root
        self.parent = parent
        
        self.x = float(root.attrib['x'])
        self.y = float(root.attrib['y'])
        self.rot = -self.findRot()
        self.lengthName = root.attrib['length']
        (self.x2,self.y2) = rotate(pinLengths[self.lengthName],0,self.rot)
        self.x2 = self.x2 + self.x
        self.y2 = self.y2 + self.y

    def draw(self,cr):
        x1 = self.x*scale
        y1 = self.y*scale
        x2 = (self.x2)*scale
        y2 = (self.y2)*scale

        cr.save()
        #applyRotationAboutPoint(cr,0,0,-self.rot)
        cr.set_source_rgb(0, 0.5, 0)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()
        cr.restore()


class Rectangle(object):
    def __init__(self,item,parent):
        self.item = item
        self.parent = parent
        
        x1 = float(item.attrib['x1'])
        y1 = float(item.attrib['y1'])
        x2 = float(item.attrib['x2'])
        y2 = float(item.attrib['y2'])

        rot = 0.0
        if hasattr(self.parent,'rot'):
            rot = self.parent.rot
        (X1,Y1) = rotate(x1,y1,(-1)*rot)
        (X2,Y2) = rotate(x2,y2,(-1)*rot)
        
        self.x1 = X1
        self.y1 = Y1
        self.x2 = X2
        self.y2 = Y2
       
    def draw(self,cr):
        x1 = min(self.x1,self.x2)*scale
        y1 = min(self.y1,self.y2)*scale
        xlen = abs(self.x1-self.x2)*scale
        ylen = abs(self.y1-self.y2)*scale
        cr.rectangle(x1,y1,xlen,ylen)
        cr.stroke()

    def flip(self):
        self.y1 = -self.y1
        self.y2 = -self.y2
        pass


import inspect, parse, math
from cairoStuff import *
from config import *
from config import sch_to_display_pixel_scale as scale
import  xml.etree.ElementTree as ET
from numpy import *
import sys,subprocess
import json
import colors

from plot import plotPng


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
        self.selectedPins = []

    def draw(self, width, height):
        '''
        Translates the canvas to x,y
        which in turn is set to the center of the selected component
        '''
        #print "I also draw."
        ## A shortcut
        cr = self.cr
        applyTranslation(cr,self.x,self.y)
        self.sheets[0].draw(self.cr)

    def processFrame(self,frame):
        '''
        This takes in a display frame and selects all instances with the same part name
        '''
        a = self.sheets[0].processFrame(frame)
        if a is not None:
            (x,y) = a
            self.moveTo(x,y)

    def moveTo(self,x,y):
        self.x = (width/2)-x*scale
        self.y = (height/2)-y*scale
    
    def loadSheets(self):
        '''
        Loads the sheets, but only the first sheet is used right now.
        '''
        a = self.getElementsWithTagName('sheet')
        for i in a:
            self.sheets.append(Sheet(i,self,self))
              

    def selectPins(self,a):
        '''
        This selects all pins that come in the list and deselects the ones that were in the previous list.
        '''
        #Handle logistical stuff that has to happen to select an instance
        for i in self.selectedPins:
            i.deselect()

        self.selectedPins = []
        for i in a:
            i.select()
            self.selectedPins.append(i)


    def selectInstances(self,a):
        '''
        This selects all instances that come in the list a
        and centers the frame about the first one in the list.
        '''
        #Handle logistical stuff that has to happen to select an instance
        if self.selectedInstances is not None:
            for i in self.selectedInstances:
                i.deselect()
        self.selectedInstances = a
        for i in a:
            i.select()
        
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
        self.measurements = []

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
        for i in self.measurements:
            i.draw(cr)


    def processFrame(self,frame):
        frame = frame.strip()
        frameDict = json.loads(frame)
        print frameDict
        if frameDict is not None:
            if frameDict['type'] == 'VDC':
                return self.processVDCFrame(frameDict)
            if frameDict['type'] == 'select':
                return self.processSelectFrame(frameDict)
            if frameDict['type'] == 'VAC':
                return self.processVACFrame(frameDict)


    def processVACFrame(self,frameDict):
        measObj = ACMeasurement(frameDict,self)
        self.measurements = []
        self.measurements.append(measObj)
        
        self.parent.selectInstances([measObj.positivePart])
        self.parent.selectPins([measObj.positivePin])
        
        return measObj.center()


    def processVDCFrame(self,frameDict):
        measObj = DCMeasurement(frameDict,self)
        self.measurements = []
        self.measurements.append(measObj)

        self.parent.selectInstances([measObj.positivePart])
        self.parent.selectPins([measObj.positivePin])

        return measObj.center()


    def processSelectFrame(self,frameDict):
        p = self.instanceHash[frameDict['partName']]
        self.parent.selectInstances(p)
        return (p[0].x,p[0].y)


class ACMeasurement(object):
    def __init__(self,frameDict,schSheet):
        self.type = frameDict['type']
        self.value = frameDict['value']
        self.valueText = '%f V'%(self.value,)
        positive = frameDict['positive']
        positiveParts = schSheet.instanceHash[positive['partName']]
    
        self.positivePart = None
        self.positivePin = None
        
        for i in positiveParts:
            if positive['pad'] in i.padHash:
                self.positivePart = i
                self.positivePin = i.padHash[positive['pad']]
                                
        self.positivePin = self.positivePart.padHash[positive['pad']]
                
        (x1,y1) = self.positivePin.centerAbsolute()
        (self.centerX,self.centerY) = (x1,y1)

        #create the plot to be displayed
        plotPng('s.png')
        self.imagesurface = cairo.ImageSurface.create_from_png('s.png')
        self.imageHeight = self.imagesurface.get_height()
    
    def center(self):
        return (self.centerX,self.centerY)
        
    def draw(self,cr):
        cr.save()
        cr.set_source_rgb(*colors.measurement)

        (x1,y1) = self.positivePin.centerAbsolute()
        
        cr.save()    # push a new context onto the stack
        cr.set_source_surface(self.imagesurface,x1*scale+60,(y1*scale)-self.imageHeight/2)
        cr.paint()
        cr.restore() 

        cr.restore()
        

class DCMeasurement(object):
    def __init__(self,frameDict,schSheet):
        self.type = frameDict['type']
        self.value = frameDict['value']
        self.valueText = '%f V'%(self.value,)
        positive = frameDict['positive']
        positiveParts = schSheet.instanceHash[positive['partName']]
    
        self.positivePart = None
        self.positivePin = None
        
        for i in positiveParts:
            if positive['pad'] in i.padHash:
                self.positivePart = i
                self.positivePin = i.padHash[positive['pad']]
                                
        self.positivePin = self.positivePart.padHash[positive['pad']]
                
        #(self.centerX,self.centerY) = ((self.positivePart.x+self.negativePart.x)/2,(self.positivePart.y+self.negativePart.y)/2)
        (x1,y1) = self.positivePin.centerAbsolute()
        (self.centerX,self.centerY) = (x1,y1)

    
    def center(self):
        return (self.centerX,self.centerY)
        
    def draw(self,cr):
        cr.save()
        cr.set_source_rgb(*colors.measurement)

        (x1,y1) = self.positivePin.centerAbsolute()
        
        cr.set_font_size(30)
        cr.select_font_face('Helvetica',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
        cr.move_to(x1*scale+60,y1*scale)
        cr.show_text(self.valueText) 

        cr.restore()


class Line(object):
    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def draw(self,cr):
        cr.move_to(self.x1,self.y1)
        cr.line_to(self.x2,self.y2)
        cr.stroke()


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
            cr.set_source_rgb(*colors.net)
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
        self.padHash = {}

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
        self.pdfProcess = None

        self.loadPart()
        self.loadDeviceset()
        self.loadDevice()
        self.loadGate()
        self.loadConnects()

    def loadDatasheet(self):
        if self.dataSheetFileName is not None:
            self.pdfProcess = subprocess.Popen([pdfCommand,datasheetDir+self.dataSheetFileName])

    def select(self):
        self.selected = True
        self.loadDatasheet()

    def closeDatasheet(self):
        try:
            self.pdfProcess.kill()
        except:
            print 'Couldnt kill the pdf process for some reason'
        
    def deselect(self):
        self.selected = False
        self.closeDatasheet()
       
    def color(self):
        if self.selected:
            return colors.partSelected
        else:
            return colors.part
       
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

    def loadDevice(self):
        a = self.devicesetElement.findall('devices/device')
        for i in a:
            if i.attrib['name'] == self.deviceName:
                self.deviceElement = i
             
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

    def absoluteCoordinates(self,x,y):
        (x1,y1) = rotate(x,y,self.rot)
        return (x1+self.x,y1+self.y)

    def loadConnects(self):
        a = self.deviceElement.findall('connects/connect')
        for i in a:
            if i.attrib['gate'] == self.gateName:
                if i.attrib['pad'] not in self.padHash:
                    if i.attrib['pin'] in self.gate.symbol.pinHash:
                        self.padHash[i.attrib['pad']] = self.gate.symbol.pinHash[i.attrib['pin']]


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
        cr.set_source_rgb(0.0,0.0,0.5)
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
        self.pinHash = {}
        
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
            t = Pin(i,self)
            self.pins.append(t)
            self.pinHash[t.name] = t
            

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
        self.name = root.attrib['name']
        self.x = float(root.attrib['x'])
        self.y = float(root.attrib['y'])
        self.rot = -self.findRot()
        self.rotName = ''
        if 'rot' in root.attrib:
            self.rotName = root.attrib['rot']

        self.lengthName = root.attrib['length']

        #Load test data to plot pretty graphs with
        self.testData = None
        if 'testData' in root.attrib:
            f = open(root.attrib['testData'],'r')
            self.testData = json.loads(f.readline())
            f.close()
            #print self.testData

        (self.x2,self.y2) = rotate(pinLengths[self.lengthName],0,self.rot)
        self.x2 = self.x2 + self.x
        self.y2 = self.y2 + self.y
        self.selected = False
        self.centerX = (self.x + self.x2)/2
        self.centerY = (self.y + self.y2)/2

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def color(self):
        if self.selected:
            return colors.pinSelected
        else:
            return colors.pin

    def centerAbsolute(self):
        return self.parent.parent.parent.absoluteCoordinates(self.centerX,self.centerY)

    def draw(self,cr):
        x1 = self.x*scale
        y1 = self.y*scale
        x2 = (self.x2)*scale
        y2 = (self.y2)*scale

        cr.save()
        #applyRotationAboutPoint(cr,0,0,-self.rot)
        cr.set_source_rgb(*self.color())
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

        rot = self.rot
        cr.select_font_face('Helvetica',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)        
        cr.move_to(x2,y2+10)
        cr.set_source_rgb(0.2,0.2,0.2)
        applyRotationAboutPoint(cr,x2,y2,-self.rot)
        if self.rotName == 'R180':
            (_,_, plusWidth, plusHeight, _, _) = cr.text_extents(self.name)
            (p,q) = cr.get_current_point()
            cr.move_to(p+plusWidth,q+plusHeight)
            applyRotationAboutPoint(cr,x2,y2,self.rot)
        cr.show_text(self.name)

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


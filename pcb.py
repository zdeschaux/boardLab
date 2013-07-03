import inspect
from cairoStuff import *
from config import *

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
    def __init__(self,eda_pcb):
        Screen.__init__( self )
        ## x,y is where I'm at
        self.x, self.y = 25, -25
        ## rx,ry is point of rotation
        self.rx, self.ry = -10, -25
        ## rot is angle counter
        self.rot = 0
        ## sx,sy is to mess with scale
        self.sx, self.sy = 0.5, 0.5

        done = False
        self.eda_pcb = eda_pcb
        self.x = -100
        self.y = -100
        self.angle = 0
        
        a = eda_pcb.GetBoundingBox()
        (self.preOffset_x,self.preOffset_y) = a.GetOrigin()
        self.elements = []
        #self.scale = float(width-(2*borderWidth))/a.GetWidth()
        self.scale = pcb_to_display_pixel_scale
        print width,borderWidth,a.GetWidth()
        print 'scale',self.scale
        
        for module in eda_pcb.GetModules():
            #This is done only once
            #OnlyOnce
            if not done:
                print ""
                print "Members for module"
                printMembers(module)
                
                print ""
                print "Members for footprint rectangle"
                printMembers(module.GetFootPrintRect())
                done = True
            #/OnlyOnce
                
            print "* Module: %s,%s at %s"%(module.GetLibRef(),module.GetReference(),module.GetPosition())
            newElement = BasicElement(module,self)
            self.elements.append(newElement)
        print ""
        self.setPositionScale(-700,-120,0)
        print self.findFiducial()


    def draw( self, width, height ):
        ## A shortcut
        cr = self.cr
        cr.save()
        
        #Draw the PCB bounding box
        a = self.eda_pcb.GetBoundingBox()
        (origin,width,height) = getOWH(a)
        relativeCoordinates = self.calculateRelativePosition(origin,width,height)
        scaledWidth = relativeCoordinates[2]
        scaledHeight = relativeCoordinates[3]

        applyTranslation(cr,100,100)
        applyRotationAboutPoint(cr,0,0,self.rot)

        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        cr.rectangle(0,0, scaledWidth, scaledHeight)
        cr.set_source_rgb(1,0,0)
        cr.stroke()
       
        for element in self.elements:
            element.draw(cr)

        cr.restore()
        #self.rot += 0.1

     
    def setPositionScale(self,x,y,angle):
        self.x = x
        self.y = y
        self.angle = angle
        #self.scale = scale
        
    def calculateRelativePosition(self,origin,width,height):
        sWidth = self.scale*width
        sHeight = self.scale*height
        s_origin = (origin[0]-self.preOffset_x,origin[1]-self.preOffset_y)
        ss_origin = (self.scale*s_origin[0],self.scale*s_origin[1])
        #final_origin = (ss_origin[0]+self.x,ss_origin[1]+self.y)
        final_origin = (ss_origin[0],ss_origin[1])
        return (final_origin[0],final_origin[1],sWidth,sHeight)
    
    def findModuleUnderMouse(self,x,y):
        for element in self.elements:
            a = element.checkUnderMouse(x,y)
 
    def findFiducial(self):
        for element in self.elements:
            if element.edaElem.GetReference() == 'VAL':
                self.fiducialPosition = element.edaElem.GetPosition() 
                return self.fiducialPosition

            

class BasicElement(object):
    def __init__(self,EDA_elem,pcb):
        self.edaElem = EDA_elem
        self.underMouse = False
        self.pcb = pcb

    def fontPosition(self):
        a = self.relativePosition()
        return (a[0],a[1])

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

    def color(self):
        if self.underMouse:
            return red
        else:
            return green

    def draw(self,cr):
        relativeCoordinates = self.relativePosition()
        (startX,startY,width,height) = relativeCoordinates
        cr.set_line_join(cairo.LINE_JOIN_BEVEL)
        cr.rectangle(startX,startY, width, height)
        cr.set_source_rgb(0,0,0)
        cr.stroke()
        
    def relativePosition(self):
        a = self.edaElem.GetFootPrintRect()
        return self.pcb.calculateRelativePosition(*getOWH(a))


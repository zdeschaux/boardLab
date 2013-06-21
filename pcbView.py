#!/usr/bin/env python
import sys
from pcbnew import *
import inspect
import pygame, tracking
from pygame.locals import *

pygame.init()

red = Color(255,0,0)
green = Color(0,255,0)
blue = Color(0,0,255)
darkBlue = Color(0,0,128)
white = Color(255,255,255)
black = Color(0,0,0)
pink = Color(255,200,200)

font = pygame.font.SysFont("Helvetica", 12)
fontColor = darkBlue

width = 1200
height = 800
borderWidth = 100
ToUnits = ToMils
FromUnits = FromMils
trackingConnection = None

def getOWH(a):
    origin = a.GetOrigin()
    end = a.GetEnd()
    width = a.GetWidth()
    height = a.GetHeight()
    return (origin,width,height)


class PCB(object):
    def __init__(self,eda_pcb):
        done = False
        self.eda_pcb = eda_pcb
        self.x = 0
        self.y = 0
        self.angle = 0
        
        a = eda_pcb.GetBoundingBox()
        (self.preOffset_x,self.preOffset_y) = a.GetOrigin()
        self.elements = []
        self.scale = float(width-(2*borderWidth))/a.GetWidth()
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
                
            print "* Module: %s,%s at %s"%(module.GetLibRef(),module.GetReference(),ToUnits(module.GetPosition()))
            newElement = BasicElement(module,self)
            self.elements.append(newElement)
        print ""
        self.setPositionScale(100,100,0)

        
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
        final_origin = (ss_origin[0]+self.x,ss_origin[1]+self.y)
        return (final_origin[0],final_origin[1],sWidth,sHeight)
    
    def draw(self,screen):
        a = self.eda_pcb.GetBoundingBox()
        (origin,width,height) = getOWH(a)
        relativeCoordinates = self.calculateRelativePosition(origin,width,height)
        pygame.draw.rect(screen,blue,relativeCoordinates,1)
        for element in self.elements:
            element.draw(screen)
    
    
    def findModuleUnderMouse(self,x,y):
        for element in self.elements:
            a = element.checkUnderMouse(x,y)

            

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

    def draw(self,screen):
        relativeCoordinates = self.relativePosition()
        pygame.draw.rect(screen,self.color(),relativeCoordinates,0)
        label = font.render(self.edaElem.GetReference(), 1, fontColor)
        screen.blit(label,self.fontPosition())

    def relativePosition(self):
        a = self.edaElem.GetFootPrintRect()
        return self.pcb.calculateRelativePosition(*getOWH(a))


def printMembers(a):
    b = inspect.getmembers(a)
    for i in b:
        print i


def drawPointer(screen,x,y):
    pygame.draw.rect(screen,blue,(x,y,10,10),0)


def pcbView(filename,useMouse=False):
    print "Loading PCB %s"%(filename)
    eda_pcb = LoadBoard(filename)
    pcb = PCB(eda_pcb)
    x = 0
    y = 0
    angle = 0

    done = False 
           
    pcb_window = pygame.display.set_mode((int(width),int(height)))
    pygame.display.set_caption('BoardLab')
    screen = pygame.display.get_surface()
    
    print "Listing Modules found in the file:"
                        
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            print "Alright, alright, I'm going. Bye!"
            sys.exit(0)

        if useMouse:
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
        else:
            a = tracking.getFrame(trackingConnection)
            if a != {}:
                x = a[2]['x']
                y = a[2]['y']
        
        screen.fill([0,0,0])
        pcb.findModuleUnderMouse(x,y)
        pcb.draw(screen)
        drawPointer(screen,x,y)
        pygame.display.update()
        #pygame.time.wait(100)
            

if __name__=="__main__":
    useMouse = False
    filename = sys.argv[1]
    if len(sys.argv) == 3:
        if sys.argv[2] == 'mouse':
            useMouse = True
    if not useMouse:
        trackingConnection = tracking.connect()
    pcbView(filename,useMouse=useMouse)
    

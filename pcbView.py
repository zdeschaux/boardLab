#!/usr/bin/env python
import sys
from pcbnew import *
import inspect
import pygame
from pygame.locals import *

pygame.init()

red = Color(255,0,0)
green = Color(0,255,0)
blue = Color(0,0,255)
darkBlue = Color(0,0,128)
white = Color(255,255,255)
black = Color(0,0,0)
pink = Color(255,200,200)

filename=sys.argv[1]

class ScalerShifter(object):
    def __init__(self,scale,preOffset,postOffset):
        self.scale = scale
        self.preOffset = preOffset
        self.postOffset = postOffset

    def rectCalc(self,rect):
        origin = (rect[0],rect[1])
        width = rect[2]
        height = rect[3]
        
        sWidth = self.scale*width
        sHeight = self.scale*height
        s_origin = (origin[0]-self.preOffset[0],origin[1]-self.preOffset[1])
        ss_origin = (self.scale*s_origin[0],self.scale*s_origin[1])
        final_origin = (ss_origin[0]+self.postOffset[0],ss_origin[1]+self.postOffset[1])
        return (final_origin[0],final_origin[1],sWidth,sHeight)


class BasicElement(object):
    def __init__(self,EDA_elem):
        self.edaElem = EDA_elem
        self.sserRect = None
        self.underMouse = False

    def rect(self,sser=None):
        a = self.edaElem.GetFootPrintRect()
        originalRect = (a.GetOrigin()[0],a.GetOrigin()[1],a.GetWidth(),a.GetHeight())
        if sser == None:
            return originalRect
        else:
            if self.sserRect == None:
                self.sserRect = sser.rectCalc(originalRect)
            return self.sserRect

    def checkUnderMouse(self,x,y):
        left = self.sserRect[0]
        top = self.sserRect[1]
        right = left + self.sserRect[2]
        bottom = top + self.sserRect[3]
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


def findModuleUnderMouse(elements,x,y):
    for element in elements:
        a = element.checkUnderMouse(x,y)


print "Loading PCB %s"%(filename)
pcb = LoadBoard(filename)

done = False 
#ToUnits = ToMM 
#FromUnits = FromMM 
ToUnits=ToMils
FromUnits=FromMils
borderWidth = 100
width = 1200

elements = []
a = pcb.GetBoundingBox()
print "Origin: %s, End:%s"%(a.GetOrigin(),a.GetEnd(),)
print "Width: %s, Height:%s"%(a.GetWidth(),a.GetHeight())

aspect_ratio = float(a.GetWidth())/a.GetHeight()

#Height is calculated by the width subtracted the border
height = (1/aspect_ratio)*(width-(2*borderWidth))
#Border is added to the height
height += (2*borderWidth)

scale = float(width-(2*borderWidth))/a.GetWidth()
pre_offset = (a.GetEnd())
post_offset = (width-borderWidth,height-borderWidth)

#Stands for scaler shift-er
sser = ScalerShifter(scale,pre_offset,post_offset)

pcb_window = pygame.display.set_mode((int(width),int(height)))
pygame.display.set_caption('BoardLab')
screen = pygame.display.get_surface()

pygame.display.update()
print "Listing Modules found in the file:"
 
for module in pcb.GetModules():
    if not done:
        print ""
        print "Members for module"
        a = inspect.getmembers(module)
        for i in a:
            print i

        print ""
        print "Members for footprint rectangle"
        a = inspect.getmembers(module.GetFootPrintRect())
        for i in a:
            print i
    done = True
    print "* Module: %s,%s at %s"%(module.GetLibRef(),module.GetReference(),ToUnits(module.GetPosition()))
    newElement = BasicElement(module)
    elements.append(newElement)
    
print ""

def drawElements(pcb,elements,sser):
    a = pcb.GetBoundingBox()
    pygame.draw.rect(screen,blue,sser.rectCalc((a.GetOrigin()[0],a.GetOrigin()[1],a.GetWidth(),a.GetHeight())),1)
    for element in elements:
        pygame.draw.rect(screen,element.color(),element.rect(sser=sser),0)

while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        print "Alright, alright, I'm going. Bye!"
        sys.exit(0)
    elif event.type == pygame.MOUSEMOTION:
        x, y = event.pos
        findModuleUnderMouse(elements,x,y)
    screen.fill([0,0,0])
    drawElements(pcb,elements,sser)
    pygame.display.update()
    #pygame.time.wait(100)


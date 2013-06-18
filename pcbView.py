#!/usr/bin/env python
import sys
from pcbnew import *
import inspect
import pygame

pygame.init()

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

filename=sys.argv[1]

class ScalerShifter(object):
    def __init__(self,scale,preOffset,postOffset):
        self.scale = scale
        self.preOffset = preOffset
        self.postOffset = postOffset

    def rectCalc(self,rect):
        origin = rect.GetOrigin()
        width = rect.GetWidth()
        height = rect.GetHeight()
        
        sWidth = self.scale*width
        sHeight = self.scale*height
        s_origin = (origin[0]-self.preOffset[0],origin[1]-self.preOffset[1])
        ss_origin = (self.scale*s_origin[0],self.scale*s_origin[1])
        final_origin = (ss_origin[0]+self.postOffset[0],ss_origin[1]+self.postOffset[1])
        return (final_origin[0],final_origin[1],sWidth,sHeight)


print "Loading PCB %s"%(filename)
pcb = LoadBoard(filename)

done = False 
#ToUnits = ToMM 
#FromUnits = FromMM 
ToUnits=ToMils
FromUnits=FromMils
borderWidth = 100
width = 1200

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

pygame.draw.rect(screen,blue,sser.rectCalc(a),1)
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
    print "BoundingBox: %s "%(module.GetBoundingBox(),)
    print "Drawings: %s "%(module.GetFootPrintRect(),)
    a = module.GetFootPrintRect()
    print "Origin: %s, End:%s"%(a.GetOrigin(),a.GetEnd(),)
    pygame.draw.rect(screen,green,sser.rectCalc(a),0)
    pygame.display.update()

print "" 

while True:
    input(pygame.event.get())
    for event in pygame.event.get():
        print event
        print even.type
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit();

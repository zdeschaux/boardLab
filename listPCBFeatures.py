#!/usr/bin/env python
import sys
from pcbnew import *
import inspect

filename=sys.argv[1]
 
pcb = LoadBoard(filename)
 
#ToUnits = ToMM 
#FromUnits = FromMM 
ToUnits=ToMils
FromUnits=FromMils

for i in inspect.getmembers(pcb):
    print i

sys.exit(0)

done = False 

if False:
    print "LISTING VIAS:"
    
    for item in pcb.GetTracks():
        print item
        if not done:
            a = inspect.getmembers(item)
            for i in a:
                print i
                done = True
                if type(item) is SEGVIA:         
                    pos = item.GetPosition()
                    drill = item.GetDrillValue()
                    width = item.GetWidth()
                    print " * Via:   %s - %f/%f "%(ToUnits(pos),ToUnits(drill),ToUnits(width))
                    
                elif type(item) is TRACK:
                    net = item.GetNet()
                    start = item.GetStart()
                    end = item.GetEnd()
                    width = item.GetWidth()
                    
                    print " * Track: %s to %s, width %f, net %s" % (ToUnits(start),ToUnits(end),ToUnits(width),net)
                    
                else:
                    print "Unknown type    %s" % type(item)
                    
                    done = False
                    print ""

print "LIST MODULES:"
 
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
    print "Footprint rectangle centre: %s "%(module.GetFootPrintRect().Centre(),)
    a = module.GetFootPrintRect()
    #print "Right %s, Size %s, Width %s, Position %s, Height %s, Origin %s, End %s"%(a.GetRight(),a.GetSize(),a.GetWidth(),a.GetPosition(),a.GetHeight(),a.GetOrigin(),a.GetEnd())
    #GetOrigin and GetEnd are enough to construct the rectangle
    print "Origin: %s, End:%s"%(a.GetOrigin(),a.GetEnd(),)

print "" 

if False:
    print "LIST ZONES:"
    
    for zone in pcb.GetSegZones():
        print zone
        print ""

if False:
    print "LISTING DRAWINGS:"
    
    for item in pcb.GetDrawings():
        if type(item) is TEXTE_PCB:
            print "* Text:    '%s' at %s"%(item.GetText(),item.GetPosition())
        elif type(item) is DRAWSEGMENT:
            print "* Drawing: %s"%item.GetShapeStr() # dir(item)
        else:
            print type(item)    
            
            print ""

if False:
    print "RATSNEST:",len(pcb.GetFullRatsnest())
    
    print dir(pcb.GetNetClasses())
    

#!/usr/bin/env python
import sys, inspect
from cairoStuff import *
from pcb import *
from config import *
import gobject, tracking


def pcbView(filename,trackingObject,useMouse=False):
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    window.set_size_request ( width, height )
    print "Loading PCB %s"%(filename)
    pcb = PCB(filename,trackingObject)
    x = 0
    y = 0
    angle = 0

    widget = pcb
    widget.show( )
    window.add( widget )
    window.present( )
    gtk.main()

if __name__=="__main__":
    useMouse = False
    filename = sys.argv[1]
    if len(sys.argv) == 3:
        if sys.argv[2] == 'mouse':
            useMouse = True
    if not useMouse:
        trackingObject = None
        if not noTrackingDebug:
            trackingObject = tracking.tracking()
            trackingObject.connect()
    pcb = pcbView(filename,trackingObject,useMouse=useMouse)

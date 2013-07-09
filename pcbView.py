#!/usr/bin/env python
import sys, inspect
from cairoStuff import *
from pcb import *
from config import *
import gobject, tracking
import threading
import time, json

class TrackingSignaller(gobject.GObject):
    def __init__(self):
        self.__gobject_init__()
        
gobject.type_register(TrackingSignaller)
gobject.signal_new("tracking_frame", TrackingSignaller, gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (str,))

def displayLoop():
    while(1):
        time.sleep(1)


class AutoLoader(object):
    def __init__(self,gtkWindow):
        self.loadingDict = {
            279:('pcb','funo.brd'),
            211:('selectTool','red'),
            107:('selectTool','green'),
            331:('selectTool','blue'),
        }

        self.objects = {}
        self.window = gtkWindow
        
        fileName = self.loadingDict[279][1] 
        print "Loading PCB %s"%(fileName,)
        self.pcb = PCB(fileName,displayCallback=displayCallback)
        self.pcb.show( )
        window.add( self.pcb )
        
    def processTrackingFrame(self,b,data):
        a = json.loads(data)
        print 'received trackingFrame',b,a
        if a != {}:
            if tracking.pcb_id in a:
                self.pcb.x = a[tracking.pcb_id]['x'] 
                self.pcb.y = a[tracking.pcb_id]['y']
                self.pcb.rot = a[tracking.pcb_id]['angle'] - self.pcb.rotBias
                self.pcb.rot = 0
            else:
                self.pcb.x = 500
                self.pcb.y = 500
                self.pcb.rot = 00
                        
            if tracking.selectTool_id in a:
                self.pcb.selectTool.activated = True
                self.pcb.selectTool.x = a[tracking.selectTool_id]['x']-12
                self.pcb.selectTool.y = a[tracking.selectTool_id]['y']+12
                a = self.pcb.findModuleUnderMouse(self.selectTool.x,self.selectTool.y)
                if a is not None:
                    self.pcb.displayCallback(a)
                    pass
                else:
                    self.selectTool.activated = False
        else:
            self.x = 00
            self.y = 00
            self.rot = 0
        


def trackingLoop(sender):
    trackingObject = tracking.tracking()
    trackingObject.connect()
    while(1):
        a = trackingObject.getFrame()
        sender.emit("tracking_frame",json.dumps(a))


def displayCallback(a):
    print a


if __name__=="__main__":
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    window.set_size_request ( width, height )

    autoLoader = AutoLoader(window)
    trackingSignaller = TrackingSignaller()
    trackingSignaller.connect("tracking_frame",autoLoader.processTrackingFrame)

    trackingThread = threading.Thread(target=trackingLoop,args=(trackingSignaller,))
    trackingThread.start()

    displayThread = threading.Thread(target=displayLoop)
    displayThread.start()

    window.present( )
    gtk.main()


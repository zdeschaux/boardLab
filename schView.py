#!/usr/bin/env python
import sys, inspect
from cairoStuff import *
from sch import *
from config import *
import gobject, tracking
import time, json, signal, socket, threading

class DisplaySignaller(gobject.GObject):
    def __init__(self):
        self.__gobject_init__()
       
gobject.type_register(DisplaySignaller)
gobject.signal_new("display_frame", DisplaySignaller, gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (str,))


class AutoLoader(object):
    def __init__(self,gtkWindow):
        self.loadingDict = {
            279:('sch','funo.sch'),
            211:('selectTool','red'),
            107:('selectTool','green'),
            331:('selectTool','blue'),
        }

        self.objects = {}
        self.window = gtkWindow
        
        fileName = self.loadingDict[279][1] 
        print "Loading PCB %s"%(fileName,)
        self.sch = SCH(fileName,displayCallback=None)
        self.sch.show( )
        window.add(self.sch)
        

if __name__=="__main__":
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    window.set_size_request ( width, height )

    autoLoader = AutoLoader(window)
    #displayThread = threading.Thread(target=displayLoop)
    #displayThread.start()

    window.present( )
    gtk.main()


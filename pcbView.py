#!/usr/bin/env python
import sys, inspect
from cairoStuff import *
from pcb import *
from config import *

def pcbView(filename,useMouse=False):
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    window.set_size_request ( width, height )
    
    print "Loading PCB %s"%(filename)
    pcb = PCB(filename)
    x = 0
    y = 0
    angle = 0

    widget = pcb
    widget.show( )
    window.add( widget )
    window.present( )
    gtk.main( )

    return pcb
    done = False 
                                   
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            print "Alright, alright, I'm going. Bye!"
            sys.exit(0)

        if useMouse:
            pygame.mouse.set_visible(False)
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
        else:
            a = trackingObject.getFrame()
            if a != {}:
                if tracking.pcb_id in a:
                    pcb.x = a[tracking.pcb_id]['x']
                    pcb.y = a[tracking.pcb_id]['y']
                    pcb.angle = a[tracking.pcb_id]['angle']

                if tracking.pointer_id in a:
                    scale = pcb_to_display_pixel_scale*camera_pixel_to_pcb_scale
                    x = int(float(a[tracking.pointer_id]['x'])*scale)
                    y = int(float(a[tracking.pointer_id]['y'])*scale)
                    print x,y
        
        screen.fill([0,0,0])
        pcb.findModuleUnderMouse(x-100,y-100)
        pcb.draw(screen)


if __name__=="__main__":
    useMouse = True
    filename = sys.argv[1]
    pcb = pcbView(filename,useMouse=useMouse)
    sys.exit(0)
    if len(sys.argv) == 3:
        if sys.argv[2] == 'mouse':
            useMouse = True
    if not useMouse:
        trackingObject = tracking.tracking()
        trackingObject.connect()

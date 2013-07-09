import pygtk
import gtk, gobject, cairo
from gtk import gdk

red = (1,0,0)
green = (0,1,0)
blue = (0,0,1)
darkBlue = (0,0,0.5)
white = (1,1,1)
black = (0,0,0)
pink = (1,0.8,0.8)

def applyRotationAboutPoint(context,x,y,rot):
    ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
    cairo.Matrix.translate(ThingMatrix,x,y)
    cairo.Matrix.rotate( ThingMatrix, rot ) # Do the rotation
    cairo.Matrix.translate(ThingMatrix,(-1)*x,(-1)*y)
    context.transform ( ThingMatrix ) # Changes the context to reflect that


def applyTranslation(context,x,y): 
    ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
    cairo.Matrix.translate(ThingMatrix,x,y)
    context.transform(ThingMatrix)


class Screen( gtk.DrawingArea ):
    """ This class is a Drawing Area"""
    def __init__(self):
        super(Screen,self).__init__()
        ## Old fashioned way to connect expose. I don't savvy the gobject stuff.
        self.set_events(gdk.BUTTON_PRESS_MASK | gdk.MOTION_NOTIFY | gdk.POINTER_MOTION_MASK)
        self.connect ( "expose_event", self.do_expose_event )
        self.connect ( "button-press-event", self.buttonPress)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(1.0,1.0,1.0))
        ## This is what gives the animation life!
        gobject.timeout_add( 50, self.tick ) # Go call tick every 50 whatsits.

    def buttonPress(self,a,b):
        print a
        print b
        print 'Button pressed!'
    
    def tick2 (self):
        self.doTick2()
        return True

    def tick ( self ):
        ## This invalidates the screen, causing the expose event to fire.
        self.alloc = self.get_allocation ( )
        rect = gtk.gdk.Rectangle ( self.alloc.x, self.alloc.y, self.alloc.width, self.alloc.height )
        self.window.invalidate_rect ( rect, True )
        return True # Causes timeout to tick again.


    ## When expose event fires, this is run
    def do_expose_event( self, widget, event ):
        self.cr = self.window.cairo_create( )
        ## Call our draw function to do stuff.
        self.draw( *self.window.get_size( ) )

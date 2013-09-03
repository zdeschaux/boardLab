#from pcbnew import *
#from cairoStuff import *
#from pcb import *
import numpy as np

#font = pygame.font.SysFont("Helvetica", 12)

darkBlue = (0.0,0.0,0.5)
fontColor = darkBlue

width = 1920
height = 1080

#width = 800
#height = 600
borderWidth = 0

trackingObject= None
noTrackingDebug = True

pcb_to_display_pixel_scale = 8.537191245945328
sch_to_display_pixel_scale = 5

displayOff = False

pcbPort = 9877

datasheetDir = '/home/pragungoyal/boardlab/datasheets/'
pdfCommand = '/usr/bin/evince-previewer'

pcbLineThickness = 0.25
viaRadius = 0.4

consecutiveClickInterval = 0.1
calibrationClickInterval = 2.0

probeTipOffset = np.array(( (-1.7940,),(-0.0061,),(-0.5408,), ))

fastrakPort = '/dev/ttyUSB0'

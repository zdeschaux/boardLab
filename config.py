#from pcbnew import *
#from cairoStuff import *
#from pcb import *


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

camera_pixel_to_pcb_scale = float(25400000)/177.5

demoFrame = {279:{'x':500.0,'y':200.0,'angle':0.0}}
displayOff = False

pcbPort = 9877

datasheetDir = '/home/pragungoyal/boardlab/datasheets/'
pdfCommand = '/usr/bin/evince-previewer'

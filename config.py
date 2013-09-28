#from pcbnew import *
#from cairoStuff import *
#from pcb import *
import numpy as np

#font = pygame.font.SysFont("Helvetica", 12)

darkBlue = (0.0,0.0,0.5)
fontColor = darkBlue

width = 900
height = 700

#width = 800
#height = 600
borderWidth = 0

pcb_to_display_pixel_scale = 8.537191245945328
sch_to_display_pixel_scale = 5

displayOff = False

pcbPort = 9877

datasheetDir = '/home/pragungoyal/boardLab/app/datasheets/'
pdfCommand = '/usr/bin/evince-previewer'

pcbLineThickness = 0.25
viaRadius = 0.4

consecutiveClickInterval = 0.1
calibrationClickInterval = 2.0

probeTipOffset = np.array(( (-45.5676,),(-0.15494,),(-13.736,), ))

fastrakPort = '/dev/ttyUSB0'
probePort = '/dev/ttyUSB0'
multimeterPort = '/dev/ttyUSB0'


calibrationDataFile = 'calibration.log'

namedPipe = './uiEvents'

noProbe = True
noMultimeter = True

from pcbnew import *
from cairoStuff import *
from pcb import *


#font = pygame.font.SysFont("Helvetica", 12)
fontColor = darkBlue

width = 1920
height = 1080
borderWidth = 0
ToUnits = ToMils
FromUnits = FromMils
trackingObject= None
noTrackingDebug = True


pcb_to_display_pixel_scale = 8.537191245945328
camera_pixel_to_pcb_scale = float(25400000)/177.5


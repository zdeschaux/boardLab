from pcbnew import *
from cairoStuff import *
from pcb import *


#font = pygame.font.SysFont("Helvetica", 12)
fontColor = darkBlue

width = 1200
height = 900
borderWidth = 0
ToUnits = ToMils
FromUnits = FromMils
trackingObject= None



pcb_to_display_pixel_scale = 5e-6
camera_pixel_to_pcb_scale = float(25400000)/177.5

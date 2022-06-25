import tecplot as tp
from tecplot.constant import ExportRegion

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()
    tp.new_layout()

frame1 = tp.active_frame()
frame1.add_text('This frame is in the\nupper left corner of the paper.',
                position=(5, 50), size=18)
frame1.width = 4
frame1.height = 4
frame1.position = (.5, .5)

frame2 = tp.active_page().add_frame()
frame2.width = 4
frame2.height = 4
frame2.add_text('This frame is in the\nlower right corner of the paper.',
                position=(5, 50), size=18)
frame2.position = (6.5, 4)

tp.export.save_png('frame_position.png', 600, supersample=3,
                   region=ExportRegion.WorkArea)

import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

circle0 = frame.add_circle((40, 50), 12, CoordSys.Frame)
circle1 = frame.add_circle((50, 50), 12, CoordSys.Frame)
circle2 = frame.add_circle((60, 50), 12, CoordSys.Frame)

circle0.fill_color = Color.Magenta
circle1.fill_color = Color.Yellow
circle2.fill_color = Color.Cyan

tp.export.save_png('circle.png', 600)

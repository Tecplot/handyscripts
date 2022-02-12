import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

rectangle0 = frame.add_rectangle((40, 45), (20, 12), CoordSys.Frame)
rectangle1 = frame.add_rectangle((50, 50), (20, 16), CoordSys.Frame)
rectangle2 = frame.add_rectangle((60, 55), (20, 20), CoordSys.Frame)

rectangle0.fill_color = Color.Magenta
rectangle1.fill_color = Color.Yellow
rectangle2.fill_color = Color.Cyan

tp.export.save_png('rectangle.png', 600)

import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

ellipse0 = frame.add_ellipse((40, 45), (10, 12), CoordSys.Frame)
ellipse1 = frame.add_ellipse((50, 50), (10, 16), CoordSys.Frame)
ellipse2 = frame.add_ellipse((60, 55), (10, 20), CoordSys.Frame)

ellipse0.fill_color = Color.Magenta
ellipse1.fill_color = Color.Yellow
ellipse2.fill_color = Color.Cyan

tp.export.save_png('ellipse.png', 600)

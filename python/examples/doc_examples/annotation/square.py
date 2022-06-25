import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

square0 = frame.add_square((40, 40), 15, CoordSys.Frame)
square1 = frame.add_square((50, 50), 15, CoordSys.Frame)
square2 = frame.add_square((60, 60), 15, CoordSys.Frame)

square0.fill_color = Color.Magenta
square1.fill_color = Color.Yellow
square2.fill_color = Color.Cyan

tp.export.save_png('square.png', 600)

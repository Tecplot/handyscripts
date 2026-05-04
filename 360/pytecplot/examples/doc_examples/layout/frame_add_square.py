import tecplot
from tecplot.constant import CoordSys

frame = tecplot.active_frame()
square = frame.add_square((0.2, 0.2), 0.1, CoordSys.Frame)

import tecplot
from tecplot.constant import CoordSys

frame = tecplot.active_frame()
rectangle = frame.add_rectangle((0.5, 0.5), (0.1, 0.2), CoordSys.Frame)

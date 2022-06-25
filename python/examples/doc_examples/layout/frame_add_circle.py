import tecplot
from tecplot.constant import CoordSys

frame = tecplot.active_frame()
circle = frame.add_circle((0.2, 0.2), 0.1, CoordSys.Frame)

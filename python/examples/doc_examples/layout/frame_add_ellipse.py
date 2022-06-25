import tecplot
from tecplot.constant import CoordSys

frame = tecplot.active_frame()
ellipse = frame.add_ellipse((0.5, 0.5), (0.1, 0.2), CoordSys.Frame)

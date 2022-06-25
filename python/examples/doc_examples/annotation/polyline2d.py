from __future__ import division
import math

import tecplot as tp
from tecplot.constant import *

# create sine-wave in frame % coordinates
xx = list(range(10, 90))
yy = [10 * math.sin(x / 5) + 50 for x in xx]
points = [(x, y) for x, y in zip(xx, yy)]

frame = tp.active_frame()

#{DOC:highlight}[
line = frame.add_polyline(points, coord_sys=CoordSys.Frame)
line.line_thickness = 2
line.color = Color.Blue
#]

tp.export.save_png('polyline2d.png', 600)

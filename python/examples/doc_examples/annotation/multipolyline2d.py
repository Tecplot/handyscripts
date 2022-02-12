from __future__ import division
import math

import tecplot as tp
from tecplot.constant import *

# create sine-wave in frame % coordinates
xx = list(range(10, 90))
yy = [10 * math.sin(x / 5) + 50 for x in xx]
points = [(x, y) for x, y in zip(xx, yy)]

# create new line with points shifted up and to the left
shifted_points = [(x + 5, y + 5) for x, y in points]

frame = tp.active_frame()

#{DOC:highlight}[
multi_line = frame.add_polyline(points, shifted_points, coord_sys=CoordSys.Frame)
multi_line.line_thickness = 2
multi_line.color = Color.Blue
#]

tp.export.save_png('multipolyline2d.png', 600)

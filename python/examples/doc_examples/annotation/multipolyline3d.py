from __future__ import division
import math

import tecplot as tp
from tecplot.constant import *

# create double-helix multi-polyline in data coordinates
zz = [z / 2000 for z in range(1000)]
xx = [0.5 * math.cos(z * 50) for z in zz]
yy = [0.5 * math.sin(z * 50) for z in zz]
points = [(x, y, z) for x, y, z in zip(xx, yy, zz)]
points_shifted = [(x, y, z + 0.02) for x, y, z in zip(xx, yy, zz)]

frame = tp.active_frame()
dataset = frame.create_dataset('Dataset Name', ['x', 'y', 'z'])
dataset.add_ordered_zone('Zone Name', (10, 10, 10))
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

#{DOC:highlight}[
line = frame.add_polyline(points, points_shifted)
line.line_thickness = 2
line.color = Color.Turquoise
#]

tp.export.save_png('multipolyline3d.png', 600)

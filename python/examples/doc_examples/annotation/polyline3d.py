from __future__ import division
import math

import tecplot as tp
from tecplot.constant import *

# create helix polyline in data coordinates
zz = [z / 2000 for z in range(1000)]
xx = [0.5 * math.cos(z * 50) for z in zz]
yy = [0.5 * math.sin(z * 50) for z in zz]
points = [(x, y, z) for x, y, z in zip(xx, yy, zz)]

frame = tp.active_frame()
dataset = frame.create_dataset('Dataset Name', ['x', 'y', 'z'])
dataset.add_ordered_zone('Zone Name', (10, 10, 10))
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

#{DOC:highlight}[
line = frame.add_polyline(points)
line.line_thickness = 2
line.color = Color.Chartreuse
#]

tp.export.save_png('polyline3d.png', 600)

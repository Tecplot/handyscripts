import numpy as np

import tecplot as tp
from tecplot.constant import *
from tecplot.data.operate import execute_equation

# Get the active frame, setup a grid (30x30x30)
# where each dimension ranges from 0 to 30.
# Add variable P to the dataset and give
# values to the data.
frame = tp.active_frame()
dataset = frame.dataset
for v in ['X','Y','Z','P']:
    dataset.add_variable(v)
zone = dataset.add_ordered_zone('Zone', (30,30,30))
xx = np.linspace(0,30,30)
for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
    zone.values(v)[:] = arr.ravel()
execute_equation('{P} = -10*{X} + {Y}**2 + {Z}**2')

# Enable 3D field plot and turn on contouring
frame.plot_type = PlotType.Cartesian3D
plot = frame.plot()
plot.show_contour = True

# get a handle of the fieldmap for this zone
fmap = plot.fieldmap(dataset.zone('Zone'))

# set the active contour group to flood by variable P
fmap.contour.flood_contour_group.variable = dataset.variable('P')
plot.contour(0).levels.reset_to_nice()

# show I and J-planes through the surface
#{DOC:highlight}[
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.IJPlanes
#]

# show only the first and last I-planes
# min defaults to 0, max defaults to -1
# we set step to -1 which is equivalent
# to the I-dimensions's max
#{DOC:highlight}[
fmap.surfaces.i_range = None,None,-1
#]

# show J-planes at indices: [5, 15, 25]
#{DOC:highlight}[
fmap.surfaces.j_range = 5,25,10
#]

# save image to file
tp.export.save_png('fieldmap_surfaces_ij.png', 600, supersample=3)

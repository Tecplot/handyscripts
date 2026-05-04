import numpy as np

import tecplot as tp
from tecplot.constant import *
from tecplot.data.operate import execute_equation

# Get the active frame, setup a grid (30x30x30)
# where each dimension ranges from 0 to 30.
# Add variables P,Q,R to the dataset and give
# values to the data.
frame = tp.active_frame()
dataset = frame.dataset
for v in ['X','Y','Z','P','Q','R']:
    dataset.add_variable(v)
zone = dataset.add_ordered_zone('Zone', (30,30,30))
xx = np.linspace(0,30,30)
for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
    zone.values(v)[:] = arr.ravel()
execute_equation('{P} = -10 * {X}    +      {Y}**2 + {Z}**2')
execute_equation('{Q} =       {X}    - 10 * {Y}    - {Z}**2')
execute_equation('{R} =       {X}**2 +      {Y}**2 - {Z}   ')

# Enable 3D field plot and turn on contouring
# with boundary faces
frame.plot_type = PlotType.Cartesian3D
plot = frame.plot()
srf = plot.fieldmap(0).surfaces
srf.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True

# get the contour group associated with the
# newly created zone
contour = plot.fieldmap(dataset.zone('Zone')).contour

# assign flooding to the first contour group
contour.flood_contour_group = plot.contour(0)
contour.flood_contour_group.variable = dataset.variable('P')
contour.flood_contour_group.colormap_name = 'Sequential - Yellow/Green/Blue'
contour.flood_contour_group.legend.show = False

# save image to PNG file
tp.export.save_png('fieldmap_contour.png', 600, supersample=3)

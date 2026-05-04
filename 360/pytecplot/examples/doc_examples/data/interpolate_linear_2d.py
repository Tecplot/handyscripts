import os
import numpy as np
import tecplot as tp
from tecplot.constant import *

# Use interpolation to merge information from two independent zones
examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
dataset = tp.data.load_tecplot(datafile)
# Get list of source zones to use later
srczones = list(dataset.zones())

fr = tp.active_frame()
plot = fr.plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = True
plot.show_edge = True

# Show two section of the plot independently
plot.contour(0).legend.show = False
plot.contour(1).legend.show = False
plot.contour(1).colormap_name = 'Diverging - Blue/Red'
for scrzone in srczones:
    plot.fieldmap(scrzone).edge.line_thickness = 0.4
plot.fieldmap(0).contour.flood_contour_group = plot.contour(1)

# export image of original data
tp.export.save_png('interpolate_2d_source.png', 600, supersample=3)

# use the first zone as the source, and get the range of (x, y)
xvar = plot.axes.x_axis.variable
yvar = plot.axes.y_axis.variable
ymin, xmin = 99999,99999
ymax, xmax = -99999,-99999
for scrzone in srczones:
    curxmin, curxmax = scrzone.values(xvar.index).minmax()
    curymin, curymax = scrzone.values(yvar.index).minmax()
    ymin = min(curymin,ymin)
    ymax = max(curymax,ymax)
    xmin = min(curxmin,xmin)
    xmax = max(curxmax,xmax)

# create new zone with a coarse grid
# onto which we will interpolate from the source zone
xpoints = 40
ypoints = 40
newzone = dataset.add_ordered_zone('Interpolated', (xpoints, ypoints))

# setup the (x, y) positions of the new grid
xx = np.linspace(xmin, xmax, xpoints)
yy = np.linspace(ymin, ymax, ypoints)
YY, XX = np.meshgrid(yy, xx, indexing='ij')
newzone.values(xvar.index)[:] = XX.ravel()
newzone.values(yvar.index)[:] = YY.ravel()

# perform linear interpolation from the source to the new zone
tp.data.operate.interpolate_linear(newzone, source_zones=srczones)

# show the new zone's data, hide the source
plot.fieldmap(newzone).show = True
plot.fieldmap(newzone).contour.show = True
plot.fieldmap(newzone).contour.flood_contour_group = plot.contour(0)
plot.fieldmap(newzone).edge.show = True
plot.fieldmap(newzone).edge.line_thickness = .4
plot.fieldmap(newzone).edge.color = Color.Orange

for scrzone in srczones:
    plot.fieldmap(scrzone).show = False

# export image of interpolated data
tp.export.save_png('interpolate_linear_2d_dest.png', 600, supersample=3)

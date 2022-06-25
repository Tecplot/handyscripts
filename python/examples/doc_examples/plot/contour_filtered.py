from os import path
import tecplot as tp
from tecplot.constant import *

# load the data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir,'SimpleData','HeatExchanger.plt')
ds = tp.data.load_tecplot(datafile)

# set plot type to 2D field plot
frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()

# show boundary faces and contours
surfaces = plot.fieldmap(0).surfaces
surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True

# by default, contour 0 is the one that's shown,
# set the contour's variable, colormap and number of levels
contour = plot.contour(0)
contour.variable = ds.variable('P(N)')

# cycle through the colormap three times and reversed
# show a faithful (non-approximate) continuous distribution
#{DOC:highlight}[
contour_filter = contour.colormap_filter
contour_filter.num_cycles = 3
contour_filter.reversed = True
contour_filter.fast_continuous_flood = False
contour_filter.distribution = ColorMapDistribution.Continuous
#]

# ensure consistent output between interactive (connected) and batch
contour.levels.reset_to_nice()

# save image to file
tp.export.save_png('contour_filtered.png', 600, supersample=3)

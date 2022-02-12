from os import path
import tecplot as tp
from tecplot.constant import *

# load the data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(datafile)

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
contour.variable = dataset.variable('T(K)')
contour.colormap_name = 'Sequential - Yellow/Green/Blue'
contour.levels.reset(9)

# turn on colormap overrides for this contour
contour_filter = contour.colormap_filter
#{DOC:highlight}[
contour_filter.show_overrides = True
#]

# turn on override 0, coloring the first 4 levels red
#{DOC:highlight}[
contour_override = contour_filter.override(0)
contour_override.show = True
contour_override.color = Color.Red
contour_override.start_level = 7
contour_override.end_level = 8
#]

# save image to file
tp.export.save_png('contour_override.png', 600, supersample=3)

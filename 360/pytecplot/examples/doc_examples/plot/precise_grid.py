from os import path
import tecplot as tp
from tecplot.constant import PlotType, LinePattern, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot(PlotType.Cartesian2D)
plot.activate()

plot.show_contour = True
plot.contour(0).colormap_name = 'Elevation - Above Ground Level'

xaxis = plot.axes.x_axis
plot.axes.preserve_scale = True
xaxis.max = xaxis.variable.values(0).max()

#{DOC:highlight}[
grid = plot.axes.precise_grid
grid.show = True
grid.size = 0.05
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('precise_grid.png', 600, supersample=3)

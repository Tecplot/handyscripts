from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)

plot.show_shade = False
plot.show_contour = True

#{DOC:highlight}[
plot.axes.auto_adjust_ranges = True
plot.axes.precise_grid.show = True
plot.axes.precise_grid.size = 0.05
#]

plot.view.fit()

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('axes_2d.png', 600, supersample=3)

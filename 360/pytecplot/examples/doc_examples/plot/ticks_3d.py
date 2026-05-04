from os import path
import tecplot as tp
from tecplot.constant import PlotType, TickDirection

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

plot.show_contour = True
plot.contour(0).legend.show = False
plot.axes.grid_area.filled = False

for axis in plot.axes:
    axis.show = True
    axis.grid_lines.show = False

#{DOC:highlight}[
    axis.ticks.length *= 4
    axis.ticks.minor_length *= 4
#]

plot.view.fit()

tp.export.save_png('ticks_3d.png', 600, supersample=3)

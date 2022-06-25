from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, AxisAlignment

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'CircularContour.plt')
dataset = tp.data.load_tecplot(infile)

plot = tp.active_frame().plot(PlotType.Cartesian2D)
plot.activate()

plot.show_contour = True
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

plot.axes.preserve_scale = True
plot.axes.x_axis.fit_range()

for ax in plot.axes:
#{DOC:highlight}[
    line = ax.line
    line.color = Color.DeepRed
    line.alignment = AxisAlignment.WithOpposingAxisValue
    line.opposing_axis_value = 0
#]
    ax.title.position = 85

plot.contour(0).levels.reset_to_nice()

tp.export.save_png('axis_line_cartesian2d.png', 600, supersample=3)

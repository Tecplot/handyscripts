from os import path
import tecplot as tp
from tecplot.constant import LinePattern, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot()

plot.axes.grid_area.fill_color = Color.Grey

for axis in (plot.axes.x_axis, plot.axes.y_axis):
    axis.show = True

    grid_lines = axis.grid_lines
    grid_lines.show = True

#{DOC:highlight}[
    minor_grid_lines = axis.minor_grid_lines
    minor_grid_lines.show = True
    minor_grid_lines.line_pattern = LinePattern.Dotted
    minor_grid_lines.color = Color.Cyan
#]

plot.view.fit()

tp.export.save_png('minor_grid_lines.png', 600, supersample=3)

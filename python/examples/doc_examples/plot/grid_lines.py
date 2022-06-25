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
#{DOC:highlight}[
    grid_lines = axis.grid_lines
    grid_lines.show = True
    grid_lines.line_pattern = LinePattern.LongDash
    grid_lines.color = Color.Cyan
#]

plot.view.fit()

tp.export.save_png('grid_lines.png', 600, supersample=3)

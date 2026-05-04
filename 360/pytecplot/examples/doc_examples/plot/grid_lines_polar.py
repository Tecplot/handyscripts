from os import path
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode, LinePattern, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.PolarLine)
plot.activate()

plot.axes.theta_axis.mode = ThetaMode.Radians
plot.axes.grid_area.filled = True
plot.axes.grid_area.fill_color = Color.Creme

for axis in plot.axes:
#{DOC:highlight}[
    grid_lines = axis.grid_lines
    grid_lines.show = True
    grid_lines.line_pattern = LinePattern.LongDash
    grid_lines.color = Color.Green
#]

for lmap in plot.linemaps():
    lmap.show_in_legend = False
    lmap.line.line_pattern = LinePattern.Solid
    lmap.line.line_thickness = 0.8

tp.export.save_png('grid_lines_polar.png', 600, supersample=3)

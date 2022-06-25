from os import path
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.PolarLine)
plot.activate()

plot.axes.theta_axis.mode = ThetaMode.Radians
plot.axes.grid_area.fill_color = Color.Creme

#{DOC:highlight}[
grid_area = plot.axes.grid_area
grid_area.filled = True
grid_area.fill_color = Color.SkyBlue
grid_area.show_border = True
#]

tp.export.save_png('grid_area_polar.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode, Color, TickDirection

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.PolarLine)
plot.activate()

plot.axes.theta_axis.mode = ThetaMode.Radians

raxis = plot.axes.r_axis
raxis.line.color = Color.Red
raxis.tick_labels.offset = -4

#{DOC:highlight}[
raxis.ticks.direction =TickDirection.Centered
raxis.ticks.line_thickness = 0.8
raxis.ticks.length = 4
raxis.ticks.minor_length = 4
#]

tp.export.save_png('ticks_radial.png', 600, supersample=3)

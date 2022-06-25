from os import path
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.PolarLine)
plot.activate()

plot.axes.theta_axis.mode = ThetaMode.Radians

raxis = plot.axes.r_axis
raxis.line.color = Color.Red
#{DOC:highlight}[
raxis.tick_labels.offset = -4
raxis.tick_labels.color = Color.Red
raxis.tick_labels.font.bold = True
#]

tp.export.save_png('tick_labels_radial.png', 600, supersample=3)

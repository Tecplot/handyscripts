from os import path
import tecplot as tp
from tecplot.constant import Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
dataset = tp.load_layout(infile)

frame = tp.active_frame()
plot = frame.plot()

#{DOC:highlight}[
plot.axes.orientation_axis.position = 15, 15
plot.axes.orientation_axis.color = Color.BrightCyan
#]

plot.axes.reset_range()
plot.view.fit()

tp.export.save_png('axes_orientation.png', 600, supersample=3)

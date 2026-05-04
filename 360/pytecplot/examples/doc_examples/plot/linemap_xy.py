from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()

#{DOC:highlight}[
lmap = plot.linemap(0)
lmap.line.line_thickness = 0.8
lmap.line.color = Color.DeepRed
lmap.y_axis.title.color = Color.DeepRed

lmap = plot.linemap(1)
lmap.show = True
lmap.y_axis_index = 1
lmap.line.line_thickness = 0.8
lmap.line.color = Color.Blue
lmap.y_axis.title.color = lmap.line.color
#]

tp.export.save_png('linemap_xy.png', 600, supersample=3)

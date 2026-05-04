from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, LinePattern

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()

lmap = plot.linemap(0)

#{DOC:highlight}[
line = lmap.line
line.color = Color.Blue
line.line_thickness = 1
line.line_pattern = LinePattern.LongDash
line.pattern_length = 2
#]

tp.export.save_png('linemap_line.png', 600, supersample=3)

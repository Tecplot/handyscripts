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
plot.show_bars = True
#]

lmap = plot.linemap(0)

#{DOC:highlight}[
bars = lmap.bars
bars.show = True
bars.size = 0.6*(100 / dataset.zone(0).num_points)
bars.fill_color = Color.Red
bars.line_color = Color.Red
bars.line_thickness = 0.01
#]

tp.export.save_png('linemap_bars.png', 600, supersample=3)

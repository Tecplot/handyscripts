from os import path
import tecplot as tp
from tecplot.constant import PlotType, FillMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'SunSpots.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
#{DOC:highlight}[
plot = frame.plot(PlotType.XYLine)
plot.activate()
plot.show_symbols = True
plot.linemap(0).symbols.fill_mode = FillMode.UseLineColor
plot.linemap(0).symbols.size = 1
#]

tp.export.save_png('plot_xyline.png', 600, supersample=3)

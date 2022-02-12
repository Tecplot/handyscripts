from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, LinePattern

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()
plot.show_symbols = True

# save image to file
tp.export.save_png('plot_line.png', 600, supersample=3)

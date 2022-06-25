from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'SunSpots.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.XYLine)
plot.activate()
#{DOC:highlight}[
plot.data_labels.show_node_labels = True
plot.data_labels.index_step = 3
#]

tp.export.save_png('line_plot_data_labels.png')

from os import path
import tecplot as tp
from tecplot.constant import LabelType, NumberFormat, PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = True
plot.contour(0).legend.show = False

plot.axes.x_axis.min = -8500
plot.axes.x_axis.max = 8200
plot.axes.y_axis.min = -400
plot.axes.y_axis.max = -150

#{DOC:highlight}[
plot.data_labels.show_node_labels = True
plot.data_labels.node_label_type = LabelType.VarValue
plot.data_labels.node_variable = dataset.variable('E')
plot.data_labels.index_step = 4
plot.data_labels.label_format.format_type = NumberFormat.Integer
plot.data_labels.show_box = False
#]

tp.export.save_png('field_plot_data_labels.png')

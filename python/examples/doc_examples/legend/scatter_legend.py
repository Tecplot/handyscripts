from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()
plot.show_scatter = True

# make space for the legend
plot.axes.viewport.right = 70
plot.axes.x_axis.min = 4
plot.axes.x_axis.max = 7

# assign some shape and color to each fieldmap
for i, fmap in enumerate(plot.fieldmaps()):
    for zone in fmap.zones:
        zone.name = 'Zone {}'.format(i)
    fmap.scatter.symbol().shape = GeomShape(i % 7)
    fmap.scatter.fill_mode = FillMode.UseSpecificColor
    fmap.scatter.fill_color = Color(i % 7)

#{DOC:highlight}[
plot.scatter.legend.show = True
plot.scatter.legend.row_spacing = 0.95
#]

tp.export.save_png('scatter_legend.png')

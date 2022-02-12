from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

plot.show_contour = True
plot.contour(0).legend.show = False

for ax in [plot.axes.x_axis, plot.axes.y_axis]:
    xaxis = plot.axes.x_axis
    ax.show = True
    ax.title.show = False
    ax.line.show_on_opposite_edge = True
    ax.ticks.show_on_opposite_edge = True

#{DOC:highlight}[
    ax.tick_labels.color = Color.Blue
    ax.tick_labels.show_on_opposite_edge = True
    ax.tick_labels.font.typeface = 'Times'
    ax.tick_labels.font.size = 8
    ax.tick_labels.font.italic = True
#]

plot.view.fit()

tp.export.save_png('tick_labels_3d.png', 600, supersample=3)

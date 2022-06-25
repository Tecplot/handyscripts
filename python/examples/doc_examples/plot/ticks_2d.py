import tecplot as tp
from os import path
from tecplot.constant import PlotType, AxisMode, AxisAlignment, TickDirection

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'CircularContour.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)

plot.show_contour = True
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

plot.axes.x_axis.line.show = False

yaxis = plot.axes.y_axis
yaxis.max = 0.15
yaxis.line.show = False
yaxis.line.alignment = AxisAlignment.WithOpposingAxisValue
yaxis.line.opposing_axis_value = 0
yaxis.tick_labels.transparent_background = True
yaxis.tick_labels.offset = -5

#{DOC:highlight}[
yticks = yaxis.ticks
yticks.direction = TickDirection.Centered
#]

for ticks in [plot.axes.x_axis.ticks, yticks]:
#{DOC:highlight}[
    ticks.auto_spacing = False
    ticks.spacing = 0.5
    ticks.minor_num_ticks = 3
    ticks.length *= 3
    ticks.line_thickness *= 2
#]

plot.view.fit()

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('ticks_2d.png', 600, supersample=3)

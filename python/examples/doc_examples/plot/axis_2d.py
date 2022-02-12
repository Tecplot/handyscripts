from os import path
import tecplot as tp
from tecplot.constant import PlotType, AxisMode, AxisTitleMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)

plot.show_contour = True

plot.axes.axis_mode = AxisMode.Independent
plot.axes.viewport.right = 75
plot.axes.preserve_scale = False

#{DOC:highlight}[
xaxis = plot.axes.x_axis
xaxis.title.text = 'Longitudinal (m)'
xaxis.title.title_mode = AxisTitleMode.UseText
xaxis.min = 3.8
xaxis.max = 5.3
xaxis.grid_lines.show = True
xaxis.grid_lines.draw_last = True

yaxis = plot.axes.y_axis
yaxis.title.text = 'Transverse (m)'
yaxis.title.title_mode = AxisTitleMode.UseText
yaxis.min = 2.8
yaxis.max = 4.3
yaxis.grid_lines.show = True
yaxis.minor_grid_lines.show = True
yaxis.minor_grid_lines.draw_last = True
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('axis_2d.png',600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, PositionMarkerBy

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.XYLine)
plot.activate()

#{DOC:highlight}[
marker = plot.axes.x_axis(0).marker_grid_line
marker.show = True
marker.position_by = PositionMarkerBy.Constant
marker.position = -0.4
marker.color = Color.Blue

marker = plot.axes.y_axis(0).marker_grid_line
marker.show = True
marker.position_by = PositionMarkerBy.Constant
marker.position = -0.88
marker.color = Color.Blue
#]

tp.export.save_png('marker_grid_line_2d.png', 600, supersample=3)

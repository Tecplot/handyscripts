from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, PositionMarkerBy

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
dataset = tp.load_layout(datafile)

plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.axes.grid_area.fill_color = Color.Grey

plot.axes.x_axis.show = True
plot.axes.y_axis.show = True

#{DOC:highlight}[
marker = plot.axes.x_axis.marker_grid_line
marker.show = True
marker.position_by = PositionMarkerBy.Constant
marker.position = 1.5
marker.color = Color.Cyan

marker = plot.axes.y_axis.marker_grid_line
marker.show = True
marker.position_by = PositionMarkerBy.Constant
marker.position = 0.5
marker.color = Color.Yellow
#]

plot.view.fit()

tp.export.save_png('marker_grid_line.png', 600, supersample=3)

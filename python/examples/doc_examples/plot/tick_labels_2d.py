from datetime import datetime
import tecplot as tp
from tecplot.constant import (PlotType, AxisMode, AxisAlignment, NumberFormat,
                              Color)

# tecplot dates are in days after Midnight, Dec 30, 1899
origin = datetime(1899, 12, 30)
start = (datetime(1955, 11,  5) - origin).days
stop  = (datetime(1985, 10, 26) - origin).days

tp.new_layout()
plot = tp.active_frame().plot(tp.constant.PlotType.Sketch)
plot.activate()

plot.axes.viewport.left = 15
plot.axes.viewport.right = 95

xaxis = plot.axes.x_axis
xaxis.show = True
xaxis.min, xaxis.max = start, stop
xaxis.line.alignment = AxisAlignment.WithViewport
xaxis.line.position = 50
xaxis.ticks.auto_spacing = False
xaxis.ticks.spacing = (stop - start) // 4
xaxis.ticks.spacing_anchor = start

xaxis.tick_labels.format.format_type = NumberFormat.TimeDate
xaxis.tick_labels.format.datetime_format = 'mmm d, yyyy'
xaxis.tick_labels.color = Color.Blue
xaxis.tick_labels.angle = 45

tp.export.save_png('tick_labels_2d.png', 600, supersample=3)

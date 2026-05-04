from datetime import datetime
import tecplot as tp
from tecplot.constant import PlotType, AxisMode, AxisAlignment, NumberFormat

tp.new_layout()
plot = tp.active_frame().plot(tp.constant.PlotType.Sketch)
plot.activate()

# setup the plot area margins
plot.axes.viewport.left = 10
plot.axes.viewport.right = 90

# show the x-axis, set the title, and alignment with the viewport
xaxis = plot.axes.x_axis
xaxis.show = True
xaxis.title.text = 'Negative numbers in parentheses'
xaxis.title.offset = 20
xaxis.line.alignment = AxisAlignment.WithViewport
xaxis.line.position = 50

# set limits, tick placement and tick label properties
xaxis.ticks.auto_spacing = False
xaxis.min, xaxis.max = -5.123e-5, 5.234e-5
xaxis.ticks.spacing = (xaxis.max - xaxis.min) / 6
xaxis.ticks.spacing_anchor = 0
xaxis.tick_labels.angle = 45
xaxis.tick_labels.offset = 3

# format the tick labels in superscript form. example: 1.234x10^5
# format negative numbers to use parentheses instead of a negative sign
#{DOC:highlight}[
xformat = xaxis.tick_labels.format
xformat.format_type = NumberFormat.SuperScript
xformat.precision = 3
xformat.show_negative_sign = False
xformat.negative_prefix = '('
xformat.negative_suffix = ')'
#]

tp.export.save_png('label_format.png', 600, supersample=3)

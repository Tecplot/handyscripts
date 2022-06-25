import tecplot as tp
from tecplot.constant import PlotType

frame = tp.active_frame()
plot = frame.plot(PlotType.Sketch)

#{DOC:highlight}[
plot.axes.x_axis.show = True
plot.axes.y_axis.show = True

plot.axes.viewport.left = 10
plot.axes.viewport.right = 90
plot.axes.viewport.bottom = 10
plot.axes.viewport.top = 90
#]

tp.export.save_png('axes_sketch.png', 600, supersample=3)

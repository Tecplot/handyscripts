import tecplot as tp
from tecplot.constant import PlotType

plot = tp.active_frame().plot(PlotType.Sketch)

viewport = plot.axes.viewport
viewport.left = 10
viewport.right = 90
viewport.bottom = 10

#{DOC:highlight}[
xaxis = plot.axes.x_axis
xaxis.show = True
xaxis.min = 0
xaxis.max = 360
xaxis.title.text = 'Angle (Degrees)'

xaxis.ticks.auto_spacing = False
xaxis.ticks.spacing = 60
#]

tp.export.save_png('axis_sketch.png', 600, supersample=3)

import tecplot as tp
from tecplot.constant import PlotType, Color

plot = tp.active_frame().plot(PlotType.Sketch)

viewport = plot.axes.viewport
viewport.left = 10
viewport.right = 90
viewport.bottom = 10

xaxis = plot.axes.x_axis
#{DOC:highlight}[
xaxis.show = True
xaxis.title.text = 'distance (m)'
xaxis.title.color = Color.DarkTurquoise
xaxis.title.offset = -7
#]

tp.export.save_png('axis_title_sketch.png', 600, supersample=3)

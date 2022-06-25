import tecplot as tp
from tecplot.constant import PlotType

frame = tp.active_frame()
#{DOC:highlight}[
plot = frame.plot(PlotType.Sketch)
#]

frame.add_text('Hello, World!', (36, 50), size=34)
#{DOC:highlight}[
plot.axes.x_axis.show = True
plot.axes.y_axis.show = True
#]

tp.export.save_png('plot_sketch.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, Units, AxisTitleMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)
plot.activate()

plot.show_contour = True

xaxis = plot.axes.x_axis
xaxis.title.title_mode = AxisTitleMode.UseText
xaxis.title.text = 'Longitudinal (m)'
xaxis.min, xaxis.max = 0, 1.2

yaxis = plot.axes.y_axis
yaxis.title.title_mode = AxisTitleMode.UseText
yaxis.title.text = 'Transverse (m)'
yaxis.min, yaxis.max = 0, 1.3

for ax in [xaxis, yaxis]:
#{DOC:highlight}[
    ax.title.font.typeface = 'Times'
    ax.title.font.bold = False
    ax.title.font.italic = True
    ax.title.font.size_units = Units.Frame
    ax.title.font.size = 7
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('font.png', 600, supersample=3)

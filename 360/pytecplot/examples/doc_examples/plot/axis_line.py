from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

plot = tp.active_frame().plot(PlotType.XYLine)
plot.activate()

for i in range(2):
    lmap = plot.linemap(i)
    lmap.show = True
    lmap.line.line_thickness = 0.6
    lmap.y_axis_index = i

#{DOC:highlight}[
    yax = plot.axes.y_axis(i)
    yax.line.color = lmap.line.color
    yax.title.color = lmap.line.color
    yax.tick_labels.color = lmap.line.color
    yax.line.line_thickness = 0.6
#]
    if i == 0:
#{DOC:highlight}[
        yax.grid_lines.show = True
        yax.grid_lines.color = lmap.line.color
#]
    elif i == 1:
#{DOC:highlight}[
        yax.minor_grid_lines.show = True
        yax.minor_grid_lines.color = lmap.line.color
#]

tp.export.save_png('axis_line.png', 600, supersample=3)

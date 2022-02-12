from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'SunSpots.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.XYLine)

plot.linemap(0).line.color = Color.DarkBlue
plot.linemap(0).line.line_thickness = 1.0

#{DOC:highlight}[
grid_area = plot.axes.grid_area
grid_area.filled = True
grid_area.fill_color = Color.SkyBlue
grid_area.show_border = True
#]

tp.export.save_png('grid_area_2d.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
dataset = tp.load_layout(infile)

frame = tp.active_frame()
plot = frame.plot()

#{DOC:highlight}[
plot.axes.x_axis.show = True
plot.axes.y_axis.show = True
plot.axes.z_axis.show = True
plot.axes.grid_area.fill_color = Color.SkyBlue
plot.axes.padding = 20
#]

plot.view.fit()

tp.export.save_png('axes_3d.png', 600, supersample=3)

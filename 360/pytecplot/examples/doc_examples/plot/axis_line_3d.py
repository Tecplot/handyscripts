from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
dataset = tp.load_layout(infile)

frame = tp.active_frame()
plot = frame.plot()

plot.show_mesh = False
plot.axes.grid_area.fill_color = Color.Grey

for ax in [plot.axes.x_axis, plot.axes.y_axis, plot.axes.z_axis]:
    ax.show = True
    ax.grid_lines.show = False
    ax.line.color = Color.Cyan
    ax.line.line_thickness = 0.2
    ax.line.show_on_opposite_edge = True

plot.view.fit()

tp.export.save_png('axis_line_3d.png', 600, supersample=3)

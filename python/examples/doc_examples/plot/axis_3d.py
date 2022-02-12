from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, AxisLine3DAssignment

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'RainierElevation.lay')
tp.load_layout(infile)

frame = tp.active_frame()
dataset = frame.dataset
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

plot.show_contour = True

plot.axes.grid_area.filled = False

#{DOC:highlight}[
axes = [plot.axes.x_axis, plot.axes.y_axis, plot.axes.z_axis]
#]
assignments = [AxisLine3DAssignment.YMinZMax,
               AxisLine3DAssignment.ZMaxXMin,
               AxisLine3DAssignment.XMaxYMin]

for ax, asgn in zip(axes, assignments):
#{DOC:highlight}[
    ax.show = True
    ax.grid_lines.show = False
    ax.title.show = False
    ax.line.show = False
    ax.line.edge_assignment = asgn

plot.axes.z_axis.grid_lines.show = True
plot.axes.y_axis.min=-2000
plot.axes.y_axis.max=1000
plot.axes.x_axis.min=-9500
plot.axes.x_axis.max=-7200
plot.axes.z_axis.min=0
plot.axes.x_axis.scale_factor=1.9
#]

plot.view.width = 7830
plot.view.alpha = 0
plot.view.theta = -147.5
plot.view.psi   = 70
plot.view.position = (1975, 15620, 115930)

tp.export.save_png('axis_3d.png', 600, supersample=3)

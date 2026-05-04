from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', '3ElementWing.lpk')
tp.load_layout(infile)

frame = tp.active_frame()
dataset = frame.dataset
plot = frame.plot(PlotType.Cartesian2D)

frame.background_color = Color.Black
for axis in plot.axes:
    axis.show = False

plot.axes.x_axis.min = -0.2
plot.axes.x_axis.max = 0.3
plot.axes.y_axis.min = -0.2
plot.axes.y_axis.max = 0.15

#{DOC:highlight}[
vect = plot.vector
vect.u_variable = dataset.variable('U(M/S)')
vect.v_variable = dataset.variable('V(M/S)')
vect.relative_length = 0.00025
vect.size_arrowhead_by_fraction = False
vect.arrowhead_size = 4
vect.arrowhead_angle = 10
#]

plot.show_contour = False
plot.show_streamtraces = False
plot.show_edge = True
plot.show_vector = True

cont = plot.contour(0)
cont.variable = dataset.variable('P(N/M2)')
cont.colormap_name = 'Diverging - Blue/Yellow/Red'
cont.levels.reset_levels(80000, 90000, 100000, 110000, 120000)

plot.fieldmaps().show = False

fmap = plot.fieldmap(3)
fmap.show = True
fmap.edge.color = Color.White
fmap.edge.line_thickness = 1
fmap.points.step = 5
fmap.vector.color = cont
fmap.vector.line_thickness = 0.5

tp.export.save_png('vector2d.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
tp.data.load_tecplot(infile)

frame = tp.active_frame()
dataset = frame.dataset
plot = frame.plot(PlotType.Cartesian2D)

for txt in frame.texts():
    frame.delete_text(txt)

vector_contour = plot.contour(0)
vector_contour.variable = dataset.variable('T(K)')
vector_contour.colormap_name = 'Magma'
vector_contour.colormap_filter.reversed = True
vector_contour.legend.show = False
base_contour = plot.contour(1)
base_contour.variable = dataset.variable('P(N/M2)')
base_contour.colormap_name = 'GrayScale'
base_contour.colormap_filter.reversed = True
base_contour.legend.show = False

vector = plot.vector
vector.u_variable = dataset.variable('U(M/S)')
vector.v_variable = dataset.variable('V(M/S)')
vector.relative_length = 1E-5
vector.arrowhead_size = 0.2
vector.arrowhead_angle = 16

#{DOC:highlight}[
ref_vector = vector.reference_vector
ref_vector.show = True
ref_vector.position = 50, 95
ref_vector.line_thickness = 0.4
ref_vector.label.show = True
ref_vector.label.format.format_type = NumberFormat.FixedFloat
ref_vector.label.format.precision = 1
ref_vector.magnitude = 100
#]

fmap = plot.fieldmap(0)
fmap.contour.flood_contour_group = base_contour
fmap.vector.color = vector_contour
fmap.vector.line_thickness = 0.4

plot.show_contour = True
plot.show_streamtraces = False
plot.show_vector = True

plot.axes.y_axis.min = -0.005
plot.axes.y_axis.max = 0.005
plot.axes.x_axis.min = -0.002
plot.axes.x_axis.max = 0.008

tp.export.save_png('vector2d_reference.png', 600, supersample=3)

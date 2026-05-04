from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.contour(0).variable = dataset.variable('U(M/S)')
plot.show_edge = True
plot.fieldmap(0).edge.edge_type = EdgeType.Creases

vectors = plot.vector
vectors.u_variable = dataset.variable('U(M/S)')
vectors.v_variable = dataset.variable('V(M/S)')
vectors.w_variable = dataset.variable('W(M/S)')

#{DOC:highlight}[
plot.show_slices = True
slice_0 = plot.slice(0)

slice_0.contour.show = True
slice_0.contour.contour_type = ContourType.Overlay  # AKA "Both lines and flood"

slice_0.effects.use_translucency = True
slice_0.effects.surface_translucency = 30

# Show an arbitrary slice
slice_0.orientation = SliceSurface.Arbitrary
slice_0.arbitrary_normal = (1, .5, 0)

slice_0.show_primary_slice = False
slice_0.show_start_and_end_slices = True
slice_0.start_position = (-.21, .05, .025)
slice_0.end_position = (1.342, .95, .475)
slice_0.show_intermediate_slices = True
slice_0.num_intermediate_slices = 3

slice_0.edge.show = True
slice_0.edge.line_thickness = 0.4
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('slice_group.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import SliceSurface, ContourType

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()

plot.show_slices = True
slice_0 = plot.slice(0)

# Use contour(0) for Flooding and contour(2) for Lines
plot.contour(0).variable = dataset.variable('P(N/m2)')
plot.contour(2).variable = dataset.variable('T(K)')
plot.contour(2).legend.show = False
#{DOC:highlight}[
slice_0.contour.show = True
slice_0.contour.flood_contour_group = plot.contour(0)
slice_0.contour.line_contour_group = plot.contour(2)
slice_0.contour.contour_type = ContourType.Overlay  # AKA "Both lines and flood"
#]

slice_0.show_primary_slice = False
slice_0.show_start_and_end_slices = True
slice_0.show_intermediate_slices = True
slice_0.start_position = (-.21, .05, .025)
slice_0.end_position = (1.342, .95, .475)
slice_0.num_intermediate_slices = 3

# ensure consistent output between interactive (connected) and batch
slice_0.contour.flood_contour_group.levels.reset_to_nice()
slice_0.contour.line_contour_group.levels.reset_to_nice()

tp.export.save_png('slice_contour.png', 600, supersample=3)

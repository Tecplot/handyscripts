from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.contour(0).variable = dataset.variable('U(M/S)')

#{DOC:highlight}[
plot.show_slices = True
slices = plot.slices(0, 1, 2)
slices.show = True

slices.contour.show = True
slices.contour.contour_type = ContourType.Overlay
slices.effects.use_translucency = True
slices.effects.surface_translucency = 70

# Show arbitrary slices
slices.orientation = SliceSurface.Arbitrary
slices.origin = (0.1, 0.2, 0)
slices[0].arbitrary_normal = (1, 0.5, 0)
slices[1].arbitrary_normal = (0.2, 1, 0)
slices[2].arbitrary_normal = (0, 0, 1)

slices.edge.show = True
slices.edge.line_thickness = 0.4
#]

plot.contour(0).levels.reset_to_nice()
plot.contour(0).legend.show = False

tp.export.save_png('slice_collection.png')

from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()

plot.show_slices = True
slice_0 = plot.slice(0)

plot.contour(0).variable = dataset.variable('T(K)')

# Vector variables must be assigned before displaying
vectors = plot.vector
vectors.u_variable = dataset.variable('U(M/S)')
vectors.v_variable = dataset.variable('V(M/S)')
vectors.w_variable = dataset.variable('W(M/S)')

#{DOC:highlight}[
slice_vector = plot.slice(0).vector
slice_vector.show = True
slice_vector.vector_type = VectorType.MidAtPoint
slice_vector.color = Color.BluePurple
#]

slice_0.effects.use_translucency = True
slice_0.effects.surface_translucency = 30

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('slice_vector.png', 600, supersample=3)

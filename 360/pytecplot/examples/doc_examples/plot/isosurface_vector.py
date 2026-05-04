import os
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.contour(0).variable = dataset.variable('T(K)')
plot.contour(1).variable = dataset.variable('P(N/m2)')
plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')
plot.vector.w_variable = dataset.variable('W(M/S)')

plot.show_isosurfaces = True
plot.contour(0).legend.show = False
plot.contour(1).legend.show = False

iso = plot.isosurface(0)
iso.definition_contour_group = plot.contour(0)
iso.contour.flood_contour_group = plot.contour(1)
iso.isosurface_values = 200
iso.show = True

iso.vector.show = True
iso.vector.line_thickness = 0.4
iso.vector.color = Color.Grey

view = plot.view
view.psi = 53.80
view.theta = -139.15
view.alpha = 0
view.position = (7.54498, 8.42026, 7.94559)
view.width = 0.551882

tp.export.save_png('isosurface_vector.png', 600, supersample=3)

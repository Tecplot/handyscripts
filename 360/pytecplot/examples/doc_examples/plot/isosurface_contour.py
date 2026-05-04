import os
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.show_isosurfaces = True
plot.contour(0).colormap_name = 'Magma'
plot.contour(0).variable = dataset.variable('Mach')
plot.contour(0).legend.show = False

iso = plot.isosurface(0)
iso.show = True
iso.definition_contour_group = plot.contour(0)
iso.isosurface_selection = IsoSurfaceSelection.OneSpecificValue
iso.isosurface_values = 1

#{DOC:highlight}[
plot.contour(1).variable = dataset.variable('Density')
iso.contour.show = True
iso.contour.contour_type = ContourType.PrimaryValue
iso.contour.flood_contour_group = plot.contour(1)
#]

view = plot.view
view.psi = 65.777
view.theta = 166.415
view.alpha = -1.05394
view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
view.width = 1.3844

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()
plot.contour(1).levels.reset_to_nice()

tp.export.save_png('isosurface_contour.png', 600, supersample=3)

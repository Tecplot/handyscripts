import tecplot
from tecplot.constant import *
import os

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
ds = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
plot = frame.plot()

# Set Isosurface to match Contour Levels of the first group.
iso = plot.isosurface(0)
iso.isosurface_selection = IsoSurfaceSelection.AllContourLevels
cont = plot.contour(0)
iso.definition_contour_group = cont
cont.colormap_name = 'Magma'

# Setup definition Isosurface layers
cont.variable = ds.variable('Mach')
cont.levels.reset_levels( [.95,1.0,1.1,1.4])
print(list(cont.levels))

# Turn on Translucency
iso.effects.use_translucency = True
iso.effects.surface_translucency = 80

# Turn on Isosurfaces
plot.show_isosurfaces = True
iso.show = True

cont.legend.show = False

view = plot.view
view.psi = 65.777
view.theta = 166.415
view.alpha = -1.05394
view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
view.width = 1.3844

tecplot.export.save_png("wing_iso.png",width=600, supersample=3)

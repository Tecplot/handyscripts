from os import path

import tecplot as tp
from tecplot.constant import LightingEffect, IsoSurfaceSelection

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.contour(0).variable = dataset.variable('U(M/S)')

plot.show_isosurfaces = True

iso = plot.isosurface(0)

iso.isosurface_selection = IsoSurfaceSelection.ThreeSpecificValues
iso.isosurface_values = (135.674706817, 264.930212259, 394.185717702)

iso.shade.use_lighting_effect = True
iso.effects.lighting_effect = LightingEffect.Paneled
iso.contour.show = True
iso.effects.use_translucency = True
iso.effects.surface_translucency = 50

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('isosurface_example.png', 600, supersample=3)

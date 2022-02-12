import os

import tecplot as tp
from tecplot.constant import LightingEffect, PlotType, SurfacesToPlot

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(datafile)
frame = dataset.frame

# Enable 3D field plot, turn on contouring and translucency
frame.plot_type = PlotType.Cartesian3D
plot = frame.plot()
plot.show_contour = True
plot.use_translucency = True

plot.contour(0).variable = dataset.variable('S')

# adjust effects for every fieldmap in this dataset
fmaps = plot.fieldmaps()
fmaps.contour.flood_contour_group = plot.contour(0)
fmaps.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

#{DOC:highlight}[
eff = fmaps.effects
eff.lighting_effect = LightingEffect.Paneled
eff.surface_translucency = 30
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

# save image to file
tp.export.save_png('fieldmap_effects3d.png', 600, supersample=3)

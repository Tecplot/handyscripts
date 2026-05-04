import tecplot as tp
from os import path
from tecplot.plot import IsosurfaceGroup
from tecplot.constant import Color, LightingEffect

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.show_isosurfaces = True
plot.contour(0).variable = dataset.variable('U(M/S)')
iso = plot.isosurface(0)

iso.contour.show = False  # Hiding the contour will reveal the shade.

#{DOC:highlight}[
iso.shade.show = True
iso.shade.color = Color.Red
iso.shade.use_lighting_effect = True
#]

iso.effects.lighting_effect = LightingEffect.Paneled

tp.export.save_png('isosurface_shade.png', 600, supersample=3)

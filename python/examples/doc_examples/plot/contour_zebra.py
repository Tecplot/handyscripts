from os import path
import numpy as np
import tecplot as tp
from tecplot.constant import Color, SurfacesToPlot

# load the data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir,'SimpleData','Pyramid.plt')
dataset = tp.data.load_tecplot(datafile)

# show boundary faces and contours
plot = tp.active_frame().plot()
surfaces = plot.fieldmap(0).surfaces
surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True
plot.show_shade = False

# set zebra filter on and make the zebra contours transparent
cont0 = plot.contour(0)
#{DOC:highlight}[
zebra = cont0.colormap_filter.zebra_shade
zebra.show = True
zebra.transparent = True
#]

# ensure consistent output between interactive (connected) and batch
cont0.levels.reset_to_nice()

tp.export.save_png('contour_zebra.png', 600, supersample=3)

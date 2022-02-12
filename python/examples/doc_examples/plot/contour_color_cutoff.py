import os
import tecplot as tp
from tecplot.constant import PlotType, SurfacesToPlot

# load the data
examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir,'SimpleData','Pyramid.plt')
dataset = tp.data.load_tecplot(datafile)

# show boundary faces and contours
plot = tp.active_frame().plot()
surfaces = plot.fieldmap(0).surfaces
surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True

# cutoff contour flooding outside min/max range
#{DOC:highlight}[
cutoff = plot.contour(0).color_cutoff
cutoff.include_min = True
cutoff.min = 0.5
cutoff.include_max = True
cutoff.max = 1.0
cutoff.inverted = True
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('contour_color_cutoff.png',600)

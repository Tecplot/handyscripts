from os import path
import tecplot as tp
from tecplot.constant import Color, ContourType, SurfacesToPlot

# load the data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir,'SimpleData','Pyramid.plt')
dataset = tp.data.load_tecplot(datafile)

# show boundary faces and contours
plot = tp.active_frame().plot()
plot.fieldmap(0).contour.contour_type = ContourType.Lines
surfaces = plot.fieldmap(0).surfaces
surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True

# set contour label style
#{DOC:highlight}[
contour_labels = plot.contour(0).labels
contour_labels.show = True
contour_labels.auto_align = False
contour_labels.color = Color.Blue
contour_labels.background_color = Color.White
contour_labels.margin = 20
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('contour_labels.png', 600, supersample=3)

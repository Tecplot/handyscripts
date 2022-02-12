from os import path
import tecplot as tp
from tecplot.constant import (ContourLineMode, ContourType,
                              SurfacesToPlot)

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

# set contour line style
#{DOC:highlight}[
contour_lines = plot.contour(0).lines
contour_lines.mode = ContourLineMode.SkipToSolid
contour_lines.step = 4
contour_lines.pattern_length = 2
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('contour_lines.png', 600, supersample=3)

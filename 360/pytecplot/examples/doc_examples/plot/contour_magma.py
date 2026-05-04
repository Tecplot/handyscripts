from os import path
import tecplot as tp
from tecplot.constant import *

# load data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir,'SimpleData','CircularContour.plt')
dataset = tp.data.load_tecplot(datafile)
plot = dataset.frame.plot()
#{DOC:highlight}[
plot.show_contour = True

contour = plot.contour(0)
contour.variable = dataset.variable('Mix')
contour.colormap_name = 'Magma'
#]

# ensure consistent output between interactive (connected) and batch
contour.levels.reset_to_nice()

# save image to file
tp.export.save_png('contour_magma.png', 600, supersample=3)

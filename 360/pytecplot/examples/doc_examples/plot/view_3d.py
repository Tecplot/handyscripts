import tecplot
import os
from tecplot.constant import *
examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
ds = tecplot.data.load_tecplot(infile)
plot = tecplot.active_frame().plot(PlotType.Cartesian3D)
plot.activate()
#{DOC:highlight}[
plot.view.width = 17.5
plot.view.alpha = 0
plot.view.theta = 125
plot.view.psi   = 65
plot.view.position = (-100, 80, 65)
#]

tecplot.export.save_jpeg('view_3D.jpeg', 600, supersample=3)

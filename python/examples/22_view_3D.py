import tecplot
import os
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
ds = tecplot.data.load_tecplot(infile)
plot = tecplot.active_frame().plot(PlotType.Cartesian3D)
plot.activate()
plot.view.width = 17.5
plot.view.alpha = 0
plot.view.theta = 125
plot.view.psi = 65
plot.view.position = (-100, 80, 65)

tecplot.export.save_png('3D_view.png', 600, supersample=3)

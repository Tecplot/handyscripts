import numpy as np
from os import path

import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()
    tp.new_layout()

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
dataset = tp.data.load_tecplot(datafile)

frame = tp.active_frame()
frame.activate()
plot = frame.plot()
plot.contour(0).variable = dataset.variable("P(N/M2)")
plot.show_contour = True
plot.contour(0).levels.reset(num_levels=11)
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

plot.axes.y_axis.min = -0.01
plot.axes.y_axis.max = 0.01
plot.axes.x_axis.min = -0.005
plot.axes.x_axis.max = 0.015

xx = np.linspace(0, 0.01, 100)
yy = np.zeros(100)
line = tp.data.extract.extract_line(zip(xx, yy))

plot.show_mesh = True
plot.fieldmap(0).mesh.show = False

frame = tp.active_page().add_frame()
frame.position = (3.0, 0.5)
frame.height = 2
frame.width = 4
plot = tp.active_frame().plot(PlotType.XYLine)
plot.activate()

plot.delete_linemaps()
lmap = plot.add_linemap('data', line, x=dataset.variable('P(N/M2)'),
                        y=dataset.variable('T(K)'))
lmap.line.line_thickness = 2.0
plot.axes.x_axis(0).title.font.size = 10
plot.axes.y_axis(0).title.font.size = 10
plot.axes.viewport.left = 20
plot.axes.viewport.bottom = 20
plot.view.fit()

tp.export.save_png("extract_line.png", region=ExportRegion.AllFrames,
                   width=600, supersample=3)

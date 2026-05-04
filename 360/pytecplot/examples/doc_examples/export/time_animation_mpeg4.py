import os

import tecplot as tp
from tecplot.constant import *

examples = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples, 'SimpleData', 'VortexShedding.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = True

plot.axes.x_axis.min = -0.002
plot.axes.x_axis.max = 0.012
plot.axes.y_axis.min = -0.006
plot.axes.y_axis.max = 0.006

#{DOC:highlight}[
tp.export.save_time_animation_mpeg4('vortex_shedding.mp4',
                                    start_time=0, end_time=0.0006,
                                    width=400, supersample=3)
#]

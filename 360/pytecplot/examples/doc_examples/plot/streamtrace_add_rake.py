import os

import tecplot
from tecplot.constant import *

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'Eddy.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D

plot = frame.plot()
plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_mesh = True
plot.show_shade = False

plot.vector.u_variable_index = 4
plot.vector.v_variable_index = 5
plot.vector.w_variable_index = 6
plot.show_streamtraces = True

streamtraces = plot.streamtraces
#{DOC:highlight}[
streamtraces.add_rake(start_position=[.5, .5, .5],
                      end_position=[20, 20, 20],
                      stream_type=Streamtrace.VolumeLine)
#]

tecplot.export.save_png('streamtrace_add_rake.png', 600, supersample=3)

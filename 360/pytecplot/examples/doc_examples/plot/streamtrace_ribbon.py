import os
import tecplot
from tecplot.constant import *

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D

plot = frame.plot()
plot.show_mesh = False
plot.show_shade = False
plot.show_edge = True
plot.fieldmap(0).edge.edge_type = EdgeType.Creases
plot.contour(0).variable = dataset.variable(3)
plot.contour(0).levels.reset_to_nice()

plot.vector.u_variable_index = 3
plot.vector.v_variable_index = 4
plot.vector.w_variable_index = 5

plot.show_streamtraces = True
#{DOC:highlight}[
plot.streamtraces.rod_ribbon.width = .03
plot.streamtraces.rod_ribbon.contour.show = True

plot.streamtraces.add_rake(start_position=(1.5, 0.1, .4),
                           end_position=(1.5, .9, 0.1),
                           stream_type=Streamtrace.VolumeRibbon,
                           num_seed_points=3)
plot.streamtraces.add_rake(start_position=(1.5, 0.1, 0.1),
                           end_position=(1.5, .9, .4),
                           stream_type=Streamtrace.VolumeRod,
                           num_seed_points=4)
#]

tecplot.export.save_png('streamtrace_ribbon.png', 600, supersample=3)

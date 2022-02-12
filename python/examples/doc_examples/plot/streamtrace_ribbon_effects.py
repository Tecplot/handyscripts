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

plot.show_mesh = False
plot.show_shade = False

plot.vector.u_variable_index = 3
plot.vector.v_variable_index = 4
plot.vector.w_variable_index = 5
plot.show_streamtraces = True
plot.streamtraces.rod_ribbon.width = .03
plot.streamtraces.rod_ribbon.shade.color = Color.Green

#{DOC:highlight}[
plot.streamtraces.rod_ribbon.effects.use_translucency = True
plot.streamtraces.rod_ribbon.effects.surface_translucency = 80
#]

plot.streamtraces.add_rake(start_position=(1.5, 0, .45),
                               end_position=(1.5, 1, 0),
                               stream_type=Streamtrace.VolumeRibbon)

tecplot.export.save_png('streamtrace_ribbon_effects.png', 600, supersample=3)

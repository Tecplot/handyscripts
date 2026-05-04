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

#{DOC:highlight}[
streamtraces = plot.streamtraces
streamtraces.color = Color.Blue

streamtraces.show_arrows = True
streamtraces.arrowhead_size = 2
streamtraces.step_size = .25
streamtraces.line_thickness = .2
streamtraces.max_steps = 100
#]

streamtraces.add_rake(start_position=(45.49, 15.32, 59.1),
                      end_position=(48.89, 53.2, 47.6),
                      stream_type=Streamtrace.SurfaceLine,
                      num_seed_points=4)


tecplot.export.save_png('streamtrace_example.png', 600, supersample=3)

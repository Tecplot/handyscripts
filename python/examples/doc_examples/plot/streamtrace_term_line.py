import tecplot
from tecplot.constant import *
import os

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian2D

plot = frame.plot()
plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')
plot.show_streamtraces = True
plot.show_shade = True
plot.fieldmap(0).shade.color = Color.LightBlue

#{DOC:highlight}[
streamtraces = plot.streamtraces
streamtraces.set_termination_line([(0.03, 0.005),
                                   (0.03, -0.005), ])

term_line = streamtraces.termination_line
term_line.active = True
term_line.show = True
term_line.color = Color.Red
term_line.line_pattern = LinePattern.Dashed
term_line.pattern_length = .5
term_line.line_thickness = .5
#]

streamtraces.add_rake(start_position=(-0.003, 0.005),
                      end_position=(-0.003, -0.005),
                      stream_type=Streamtrace.TwoDLine,
                      num_seed_points=10)

plot.axes.y_axis.min = -0.02
plot.axes.y_axis.max = 0.02
plot.axes.x_axis.min = -0.01
plot.axes.x_axis.max = 0.04

tecplot.export.save_png('streamtrace_term_line.png', 600, supersample=3)

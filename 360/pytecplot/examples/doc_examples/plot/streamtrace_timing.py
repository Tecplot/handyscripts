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


streamtraces = plot.streamtraces
streamtraces.show_markers = True
#{DOC:highlight}[
timing = streamtraces.timing
timing.anchor = 0
timing.delta = 0.0001
#]

streamtraces.marker_size = 1.5
streamtraces.marker_symbol().shape =GeomShape.RTri
streamtraces.marker_color = Color.Mahogany

streamtraces.add_rake(start_position=(-0.003, 0.005),
                      end_position=(-0.003, -0.005),
                      stream_type=Streamtrace.TwoDLine,
                      num_seed_points=10)


plot.axes.y_axis.min = -0.02
plot.axes.y_axis.max = 0.02
plot.axes.x_axis.min = -0.008
plot.axes.x_axis.max = 0.04

tecplot.export.save_png('streamtrace_timing.png', 600, supersample=3)

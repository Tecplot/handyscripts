import tecplot
from tecplot.constant import *
import os

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian2D

# Setup up vectors and background contour
plot = frame.plot()
plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')
plot.contour(0).variable = dataset.variable('T(K)')
plot.show_streamtraces = True
plot.show_contour = True
plot.fieldmap(0).contour.show = True

# Add streamtraces and set streamtrace style
streamtraces = plot.streamtraces
streamtraces.add_rake(start_position=(-0.003, 0.005),
                      end_position=(-0.003, -0.005),
                      stream_type=Streamtrace.TwoDLine,
                      num_seed_points=10)

streamtraces.show_arrows = False
streamtraces.line_thickness = .4

plot.axes.y_axis.min = -0.02
plot.axes.y_axis.max = 0.02
plot.axes.x_axis.min = -0.008
plot.axes.x_axis.max = 0.04

tecplot.export.save_png('streamtrace_2D.png', 600, supersample=3)

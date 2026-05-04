import os
import tecplot
from tecplot.constant import *
from tecplot.plot import Cartesian3DFieldPlot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

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

streamtrace = plot.streamtraces
streamtrace.color = Color.Green

streamtrace.show_paths = True
streamtrace.show_arrows = True
streamtrace.arrowhead_size = 3
streamtrace.step_size = .25
streamtrace.line_thickness = .4
streamtrace.max_steps = 10

# Streamtraces termination line:
streamtrace.set_termination_line([(-25.521, 39.866),
                                  (-4.618, -11.180)])

# Streamtraces will stop at the termination line when active
streamtrace.termination_line.active = True

# We can also show the termination line itself
streamtrace.termination_line.show = True
streamtrace.termination_line.color = Color.Red
streamtrace.termination_line.line_thickness = 0.4
streamtrace.termination_line.line_pattern = LinePattern.LongDash

# Markers
streamtrace.show_markers = True
streamtrace.marker_color = Color.Blue
streamtrace.marker_symbol_type = SymbolType.Geometry
streamtrace.marker_symbol().shape = GeomShape.Diamond

# Add surface line streamtraces
streamtrace.add_rake(start_position=(45.49, 15.32, 59.1),
                     end_position=(48.89, 53.2, 47.6),
                     stream_type=Streamtrace.SurfaceLine)


tecplot.export.save_png('streamtrace_line_example.png', 600, supersample=3)

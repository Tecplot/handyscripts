import os
import tecplot
from tecplot.constant import *
import numpy as np

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D

plot = frame.plot()
plot.contour(0).variable = dataset.variable('P(N/m2)')
plot.contour(0).levels.reset_to_nice()
plot.contour(0).legend.show = False

plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')
plot.vector.w_variable = dataset.variable('W(M/S)')

# Goal: create a grid of 12 stream trace ribbons on a slice
x_slice_location = .79
y_start = .077
y_end = .914
z_start = .052
z_end = .415

num_left_right_slices = 4  # Must be >= 2
num_top_bottom_slices = 3  # Must be >= 2


# Show and add a slice.
plot.show_slices = True
slice_0 = plot.slice(0)

# Set the x position of the slice.
slice_0.origin = [x_slice_location, 0, 0]

slice_0.contour.show = True

plot.show_streamtraces = True
streamtraces = plot.streamtraces
streamtraces.show_paths = True

rod = streamtraces.rod_ribbon
rod.width = .03
rod.contour.show = True


for y in np.linspace(y_start, y_end, num=num_left_right_slices):
    for z in np.linspace(z_start, z_end, num=num_top_bottom_slices):
        streamtraces.add([x_slice_location,y,z], Streamtrace.VolumeRibbon)

tecplot.export.save_png('streamtrace_ribbon_example.png', 600, supersample=3)

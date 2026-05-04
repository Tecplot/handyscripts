"""PyTecplot Example: Probe at position

This example shows how to assign specific variables to
the axes of the active plot and probe the dataset at
a point using these assignments.
"""
from os import path
import tecplot as tp

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# suppress warning dialog about aspect ratio
tp.macro.execute_command("$!Interface EnableWarnings=FALSE")

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'Eddy.plt')

dataset = tp.data.load_tecplot(datafile)
plot = tp.active_frame().plot()

# Set axes of plot (X,Y,Z) to variables (U,V,W) in dataset
plot.axes.x_axis.variable = dataset.variable('U')
plot.axes.y_axis.variable = dataset.variable('V')
plot.axes.z_axis.variable = dataset.variable('W')

# probe near the center of the data in (U,V,W)
result = tp.data.query.probe_at_position(0, 0, 10)

# get value of variable C at the probed point
c = result.data[dataset.variable('C').index]

# should print:
#   C(U=0, V=0, W=10) = 1.62
print('C(U=0, V=0, W=10) = {:.2f}'.format(c))

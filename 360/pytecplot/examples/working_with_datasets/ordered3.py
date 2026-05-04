"""Ordered Data Creation (Part 3)

3D Ordered Volume Data

This example creates a curved volume mesh using a rank-three ordered zone with
dimensions :math:`(4,5,10)`. We use the `numpy` library to generate the mesh
arrays and for most of the calculations.

The `numpy.meshgrid()` method takes arrays in the order they will be indexed.
The "matrix" (ij) indexing is used with the edge arrays in reversed order,
putting the fastest dimension (:math:`x`) last. The shape that PyTecplot
expects is then the reverse of the Numpy array's shape attribute.

"""
import numpy as np

import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# Outer edges of mesh
x = np.linspace(0, 1, 2)
y = np.linspace(0, 1, 3)
z = np.linspace(0, 3, 5)

# Create (x,y,z) mesh with indexing (i,j,k) = (2,3,5)
Z, Y, X = np.meshgrid(z, y, x, indexing='ij')
shape = Z.shape[::-1]

# Adjust x position to vary along z
X += np.sin(Z)

# Set the values at each node
scalar_data = np.sqrt(Y**2 + Z**2)

# Add some noise just for fun, fixing the random seed for this example
np.random.seed(1)
scalar_data += np.random.normal(0, 0.2, scalar_data.shape)

# Setup dataset and zone
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_ordered_zone(name='Ordered Float (4,5,10) Nodal', shape=shape)

# Fill in node locations
z.values('x')[:] = np.ravel(X)
z.values('y')[:] = np.ravel(Y)
z.values('z')[:] = np.ravel(Z)

# Set the scalar data
z.values('s')[:] = np.ravel(scalar_data)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('ordered3.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).variable = ds.variable('s')
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous
plot.contour(0).levels.reset_to_nice(10)

plot.show_edge = True
plot.show_slices = True

# Show five Z-slices, evenly spaced
slice = plot.slice(0)
slice.show_primary_slice = False
slice.show_start_and_end_slices = True
slice.show_intermediate_slices = True
slice.orientation = SliceSurface.KPlanes
slice.start_position = 0,0,0
slice.end_position = 0,0,4
slice.num_intermediate_slices = 3

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 20.6
plot.view.width = 4.178
plot.view.psi = 64.59
plot.view.theta = -159.15
plot.view.alpha = 0
plot.view.position = (7.33, 17.955, 10.42)

tp.export.save_png('ordered3.png', 600, supersample=3)

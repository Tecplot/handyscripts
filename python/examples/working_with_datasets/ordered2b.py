"""Ordered Data Creation (Part 2b)

2D Ordered Surface Data

This almost exactly the same data as in Part 2a, however we use the numpy
library to create the grid from a pair of 1D arrays. The difference is only
that the square-root calculations are good to several more significant figures
so the resulting image is slightly different.

The `numpy.meshgrid()` method takes arrays in the order they will be indexed.
The "matrix" (ij) indexing is used with the edge arrays in reversed order,
placing the fastest dimension (:math:`x`) last. The shape that PyTecplot
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

# Positions along x and y of the grid to be created
x = np.linspace(0, 1, 2)
y = np.linspace(0, 2, 3)

# Create (x,y) mesh with indexing (i,j) = (2,3)
Y, X = np.meshgrid(y, x, indexing='ij')
shape = X.shape[::-1]

# Set z position and scalar values at nodes
Z = np.sqrt(X**2 + Y**2)
scalar_data = np.sqrt(X**2 + Y**2 + Z**2)

# Setup dataset and zone
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_ordered_zone(name='Ordered Float (2,3) Nodal', shape=shape)

# Fill in node locations
z.values('x')[:] = np.ravel(X)
z.values('y')[:] = np.ravel(Y)
z.values('z')[:] = np.ravel(Z)

# Set the scalar data
z.values('s')[:] = np.ravel(scalar_data)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('ordered2b.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous

for ax in plot.axes:
    ax.show = True

plot.show_contour = True
plot.show_mesh = True
plot.show_scatter = True
plot.use_translucency = True

fmap = plot.fieldmap(z)
fmap.scatter.symbol().shape = GeomShape.Sphere
fmap.scatter.color = plot.contour(0)
fmap.mesh.line_thickness = 0.4
fmap.mesh.color = plot.contour(0)

fmap = plot.fieldmap(z)
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.All
fmap.effects.surface_translucency = 40

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 16.4
plot.view.width = 3.81
plot.view.psi = 77.4
plot.view.theta = 51.6
plot.view.alpha = 0
plot.view.position = (-11.8, -9.21, 4.78)

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('ordered2b.png', 600, supersample=3)

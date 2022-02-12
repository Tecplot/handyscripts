"""Ordered Data Creation (Part 2a)

2D Ordered Surface Data

Here we present a rank-two (surface), ordered dataset in :math:`(x,y,z)` space.
The nodes are a "mesh grid" in :math:`(x,y)` where we set the z-coordinate to
:math:`\sim\sqrt{x**2 + y**2}`. After the transposition, the resulting grid
coordinates look like this::

    X = [[0, 1], [0, 1  ], [0, 1  ]]
    Y = [[0, 0], [1, 1  ], [2, 2  ]]
    Z = [[0, 1], [1, 1.4], [2, 2.2]]

    scalar_data = [[0.0, 1.4], [1.4, 2.0], [2.8, 3.2]]

Here we show the :math:`(i,j)` indices of the nodes created::

        (0,2)----(1,2)
          |        |
          |        |
          |        |
          |        |
        (0,1)----(1,1)
          |        |
          |        |
    y     |        |
          |        |
    ^   (0,0)----(1,0)
    |
    +--> x

The methods used here are very inefficient and we suggest you use a python
library like `numpy` to create the mesh (see Part 2b).
"""
import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

def components(data):
    """Separate positions into 3D mesh grid components"""
    return [[[b[i] for b in a] for a in nodes] for i in [0,1,2]]

def flatten(data):
    """Flatten nested list"""
    return [item for sublist in data for item in sublist]

# (x,y,z) node positions
nodes = [[[0, 0, 0], [1, 0, 1  ]],
         [[0, 1, 1], [1, 1, 1.4]],
         [[0, 2, 2], [1, 2, 2.2]]]

# Separate nodes into X, Y, Z, preserving array shape
X, Y, Z = components(nodes)

# scalar value for each node
scalar_data = [[0.0, 1.4],
               [1.4, 2.0],
               [2.8, 3.2]]

# Setup dataset and zone
shape = (len(nodes[0]), len(nodes))
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_ordered_zone(name='Ordered Float (2,3) Nodal', shape=shape)

# Fill in node locations
z.values('x')[:] = flatten(X)
z.values('y')[:] = flatten(Y)
z.values('z')[:] = flatten(Z)

# Set the scalar data
z.values('s')[:] = flatten(scalar_data)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('ordered2a.dat')


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

tp.export.save_png('ordered2a.png', 600, supersample=3)

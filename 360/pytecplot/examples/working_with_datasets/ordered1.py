"""Ordered Data Creation (Part 1)

1D Ordered Data

Here we create a rank-one, 3-node, ordered dataset in :math:`(x, y, z)` space.
The node locations are created as a list of coordinates, but are then
"transposed" into lists of :math:`x`, :math:`y` and :math:`z` separately when
copying the data into Tecplot::

    Nodes:
            2
           ,  (2,2,2)
           ,
          ,
          ,
         1
        /  (1,1,0.5)
       /
      /
     0
       (0,0,0)

"""
import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# List of (x,y,z) node positions
nodes = (
    (0, 0, 0  ),
    (1, 1, 0.5),
    (2, 2, 2  ))

# Scalar value at nodes
scalar_data = (0, 1, 2)

# Setup dataset and zone
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_ordered_zone(name='Ordered Float (3,) Nodal', shape=len(nodes))

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set the scalar data
z.values('s')[:] = scalar_data

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('ordered1.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous

for ax in plot.axes:
    ax.show = True

plot.show_mesh = True
plot.show_scatter = True

fmap = plot.fieldmap(z)
fmap.scatter.symbol().shape = GeomShape.Sphere
fmap.scatter.color = plot.contour(0)
fmap.mesh.line_thickness = 0.4
fmap.mesh.color = plot.contour(0)

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 20
plot.view.width = 4.5
plot.view.psi = 71
plot.view.theta = -168
plot.view.alpha = -0.03
plot.view.position = (4.58, 19.8, 7.52)

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('ordered1.png', 600, supersample=3)

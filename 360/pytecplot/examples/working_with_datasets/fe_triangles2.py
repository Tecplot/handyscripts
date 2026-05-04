"""Triangle Finite-element Data Creation (Part 2)

This example puts two triangles, exactly as in Part 1, but the nodes on the
shared face are duplicated. This means the Tecplot Engine will not be able to
identify the face neighbors and will have to be specified by hand. It turns out
for local face neighbors, that it is more efficient to add elements to make the
face neighbor connection than to introduce individual face neighbors so we add
two elements to the connectivity list below.

The data created looks like this::

    Node positions (x,y,z):

                   (1,1,1)
                  *
                 / \
                /   \
     (0,1,.5)  *-----*  (1,0,.5)
                \   /
                 \ /
                  *
                   (0,0,0)

The two triangles will have separate nodes at the shared locations::

    Nodes:
                       5
        Element 1:    / \
                     /   \
                    4-----3
                    2-----1
                     \   /
        Element 0:    \ /
                       0

To hide the coincident edge, we add two elements in between the triangles
instead of specifying face neighbors as we would normally do if the two
triangles are in different zones (see Part 3):

                       5
            Element 1 / \
                     /   \
                    4-----3
                    |    /|
          Element 3 |   / |
                    |  /  |
                    | /   | Element 2
                    |/    |
                    2-----1
                     \   /
            Element 0 \ /
                       0

"""
import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# (x, y, z) locations of nodes
nodes = (
    (0, 0, 0  ), # node 0
    (1, 0, 0.5), # node 1
    (0, 1, 0.5), # ...
    (1, 0, 0.5),
    (0, 1, 0.5),
    (1, 1, 1  ))

# (n0, n1, n2) node indexes which make up triangles
# Notice no two faces have the same connecting nodes (globally)
conn = (
    (0, 1, 2), # element 0 consisting of faces (node connections) 0-1, 1-2, 2-0
    (3, 5, 4),
    (1, 3, 2), # elements 2 and 3 are created to indicate elements 0 and 1 are
    (2, 3, 4), # face neighbors
    )

# scalar value at the nodes
scalar_data = (0, 1, 2, 1, 2, 3)

# Create the dataset and zones
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (4,2) Nodal',
                    num_points=len(nodes), num_elements=len(conn))

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set the nodemap
z.nodemap[:] = conn

# Set the scalar data
z.values('s')[:] = scalar_data

################################################################################
# Local face neighbors for classic FE zone types are more efficiently
# specified with the node/connectivity map (elements 2 and 3 in this example)
# This code is fine, but it may cause problems with contour flooding in 3D
'''
# element face neighbors
neighbors = (
    (None, 1, None),
    (None, None, 0))

# Setting face neighbors
z.face_neighbors.set_neighbors(neighbors, obscures=True)
'''
################################################################################

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('fe_triangles2.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous

for ax in plot.axes:
    ax.show = True

plot.show_mesh = False
plot.show_contour = True
plot.show_edge = True
plot.use_translucency = True

fmap = plot.fieldmap(z)
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.All
fmap.effects.surface_translucency = 40

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10
plot.view.width = 2
plot.view.psi = 80
plot.view.theta = 30
plot.view.alpha = 0
plot.view.position = (-4.2, -8.0, 2.3)

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
plot.fieldmap(z).mesh.line_pattern = LinePattern.Dashed

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('fe_triangles2.png', 600, supersample=3)

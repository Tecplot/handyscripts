"""Triangle Finite-element Data Creation (Part 4)

Building on the examples found in Parts 1-3, we create a set of triangles
requiring "one-to-many" face neighbor connections.

The data created looks like this::

    Node positions (x,y,z):

          (-.2,-.2,1)         (.2,.2,1)
                      4-----5
                     / \   / \
                    /   \ /   \
     (-.4,-.4,.5)  1-----2-----3  (.4,.4,.5)
                    \         /
                     \       /
                      \     /
                       \   /
                        \ /
                         0  (0,0,0)

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
    ( 0  ,  0  , 0  ),
    (-0.4, -0.4, 0.5),
    ( 0  ,  0  , 0.5),
    ( 0.4,  0.4, 0.5),
    (-0.2, -0.2, 1  ),
    ( 0.2,  0.2, 1  ))

# scalar value at the nodes
scalar_data = (0, 1, 2, 3, 4, 5)

# (n0, n1, n2) node indexes which make up triangles
conn = (
    (0, 3, 1),
    (1, 2, 4),
    (2, 3, 5),
    (2, 5, 4))

# Face neighbors
neighbors = (
    (None, [1,2], None),
    (0, None, None),
    (0, None, None),
    (None, None, None))

# Obscuration of faces can be set for each connection
obscures = (True, True, True, False)

# Create the dataset and zones
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (6,4) Nodal',
                    num_points=len(nodes), num_elements=len(conn),
                    face_neighbor_mode=FaceNeighborMode.LocalOneToMany)

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set the nodemap
z.nodemap[:] = conn

# Set the scalar data
z.values('s')[:] = scalar_data

# Setting face neighbors
z.face_neighbors.set_neighbors(neighbors, obscures=obscures)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('fe_triangles4.dat')


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
plot.view.width = 1.75
plot.view.psi = 76.3
plot.view.theta = 112
plot.view.alpha = -0.65
plot.view.position = (-9.1, 3.5, 2.9)

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
plot.fieldmap(z).mesh.line_pattern = LinePattern.Dashed

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('fe_triangles4.png', 600, supersample=3)

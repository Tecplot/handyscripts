"""Triangle Finite-element Data Creation (Part 5)

In this example, we separate the triangles created in Part 4 into two zones
to illustrate the use of global one-to-many face neighbor specification.

The data created looks like this::

    Node positions (x,y,z):

        Zone 1:

              (-.2,-.2,1)         (.2,.2,1)
                          3-----4
                         / \   / \
                        /   \ /   \
         (-.4,-.4,.5)  0-----1-----2  (.4,.4,.5)


        Zone 0:

         (-.4,-.4,.5)  1-----------2  (.4,.4,.5)
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

# Zone 0 (single triangle)
# (x, y, z) locations of nodes
nodes0 = (
    ( 0  ,  0  , 0  ),
    (-0.4, -0.4, 0.5),
    ( 0.4,  0.4, 0.5))

# scalar value at the nodes
scalar_data0 = (0, 1, 3)

# (n0, n1, n2) node indexes which make up triangles
conn0 = ((0, 2, 1),)

# Face neighbors for zonne 0
neighbors0 = ((None, [0,1], None),)
neighbor_zones0 = ((None, [1,1], None),)
obscures0 = (True,)

# Zone 1 (three triangles)
# (x, y, z) locations of nodes
nodes1 = (
    (-0.4, -0.4, 0.5),
    ( 0  ,  0  , 0.5),
    ( 0.4,  0.4, 0.5),
    (-0.2, -0.2, 1  ),
    ( 0.2,  0.2, 1  ))

# scalar value at the nodes
scalar_data1 = (1, 2, 3, 4, 5)

# (n0, n1, n2) node indexes which make up triangles
conn1 = (
    (0, 1, 3),
    (1, 2, 4),
    (1, 4, 3))

# Face neighbors for zone 1
neighbors1 = (
    (0, None, None),
    (0, None, None),
    (None, None, None))
neighbor_zones1 = (
    (0, None, None),
    (0, None, None),
    (None, None, None))
obscures1 = (True, True, False)

# Create the dataset and zones
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z0 = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (3,1) Nodal',
                    num_points=len(nodes0), num_elements=len(conn0),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToMany)
z1 = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (5,3) Nodal',
                    num_points=len(nodes1), num_elements=len(conn1),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToMany)

# Fill in and connect first triangle
z0.values('x')[:] = [n[0] for n in nodes0]
z0.values('y')[:] = [n[1] for n in nodes0]
z0.values('z')[:] = [n[2] for n in nodes0]
z0.nodemap[:] = conn0
z0.values('s')[:] = scalar_data0

# Fill in and connect second triangle
z1.values('x')[:] = [n[0] for n in nodes1]
z1.values('y')[:] = [n[1] for n in nodes1]
z1.values('z')[:] = [n[2] for n in nodes1]
z1.nodemap[:] = conn1
z1.values('s')[:] = scalar_data1

# Set face neighbors
z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, obscures0)
z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, obscures1)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('fe_triangles5.dat')


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

fmaps = plot.fieldmaps()
fmaps.surfaces.surfaces_to_plot = SurfacesToPlot.All
fmaps.effects.surface_translucency = 40

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10
plot.view.width = 1.75
plot.view.psi = 76.3
plot.view.theta = 112
plot.view.alpha = -0.65
plot.view.position = (-9.1, 3.5, 2.9)

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
fmaps.mesh.line_pattern = LinePattern.Dashed

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('fe_triangles5.png', 600, supersample=3)

"""Triangle Finite-element Data Creation (Part 3)

This example puts two triangles, exactly as in Part 2, but in two different
zones. Global one-to-one face neighbors are then used to stitch the two
triangles into a quad.

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
                       2
        Zone 1:       / \
                     /   \
                    1-----0
                    2-----1
                     \   /
        Zone 0:       \ /
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

# Triangle 0
nodes0 = (
    (0, 0, 0  ),
    (1, 0, 0.5),
    (0, 1, 0.5))
scalar_data0 = (0, 1, 2)
conn0 = ((0, 1, 2),)

# neighboring element indices
neighbors0 = ((None, 0, None),)

# neighboring zone indices
neighbor_zones0 = ((None, 1, None),)

# Triangle 1
nodes1 = (
    (1, 0, 0.5),
    (0, 1, 0.5),
    (1, 1, 1  ))
scalar_data1 = (1, 2, 3)
conn1 = ((0, 1, 2),)

# neighboring element indices
neighbors1 = ((0, None, None),)

# neighboring zone indices
neighbor_zones1 = ((0, None, None),)

# Create the dataset and zones
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z0 = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (3,1) Nodal 0',
                    num_points=len(nodes0), num_elements=len(conn0),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)
z1 = ds.add_fe_zone(ZoneType.FETriangle,
                    name='FE Triangle Float (3,1) Nodal 1',
                    num_points=len(nodes1), num_elements=len(conn1),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)

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
z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, obscures=True)
z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, obscures=True)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('fe_triangles3.dat')


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

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10
plot.view.width = 2
plot.view.psi = 80
plot.view.theta = 30
plot.view.alpha = 0
plot.view.position = (-4.2, -8.0, 2.3)

fmaps = plot.fieldmaps()
fmaps.surfaces.surfaces_to_plot = SurfacesToPlot.All
fmaps.effects.surface_translucency = 40

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
fmaps.mesh.line_pattern = LinePattern.Dashed

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('fe_triangles3.png', 600, supersample=3)

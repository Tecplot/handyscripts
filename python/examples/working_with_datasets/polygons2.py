"""Polygonal Finite-element Data Creation (Part 2)

This script creates a quad of two triangles just as in Part 1, however they are
placed into two different zones. Boundary connections are then made to stitch
the two triangles together.

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
                       1
        Zone 1:       / \
                     /   \
                    2-----0
                    2-----1
                     \   /
        Zone 0:       \ /
                       0

The left/right element indices are zero-based. A value of :math:`-1` indicates
no neighboring element while values :math:`(-2, -3, -4 ...)` indicate indices
into the boundary elements array :math:`(0, 1, 2 ...)`.

"""
import itertools as it

import tecplot as tp
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# First Triangle
# Nodes are in (x,y,z)
nodes0 = ((0, 0, 0), (1, 0, 0.5), (0, 1, 0.5))
scalar_data0 = (0, 1, 2)

# Triangle faces (lines)
faces0 = ((0, 1), (1, 2), (2, 0))

# The (left elements, right elements) adjacent to each face
elements0 = ((0, 0, 0), (-1, -2, -1))

# Get the number of elements by the maximum index in elements0
num_elements0 = 1

# One boundary element neighboring the
# first element (index 0)
# of the second zone (index 1)
boundary_elems0 = ((0,),)
boundary_zones0 = ((1,),)

# Second Triangle
nodes1 = ((1, 0, 0.5), (1, 1, 1), (0, 1, 0.5))
scalar_data1 = (1, 3, 2)
faces1 = ((0, 1), (1, 2), (2, 0))
elements1 = ((0, 0, 0), (-1, -1, -2))
num_elements1 = 1

# One boundary element neighboring the
# first element (index 0)
# of the first zone (index 0)
boundary_elems1 = ((0,),)
boundary_zones1 = ((0,),)

# Create the dataset and zones
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z0 = ds.add_poly_zone(ZoneType.FEPolygon,
                      name='0: FE Polygon Float (3,1,3) Nodal',
                      num_points=len(nodes0),
                      num_elements=num_elements0,
                      num_faces=len(faces0))
z1 = ds.add_poly_zone(ZoneType.FEPolygon,
                      name='1: FE Polygon Float (3,1,3) Nodal',
                      num_points=len(nodes1),
                      num_elements=num_elements1,
                      num_faces=len(faces1))

# Fill in and connect first triangle
z0.values('x')[:] = [n[0] for n in nodes0]
z0.values('y')[:] = [n[1] for n in nodes0]
z0.values('z')[:] = [n[2] for n in nodes0]
z0.values('s')[:] = scalar_data0

# Fill in and connect second triangle
z1.values('x')[:] = [n[0] for n in nodes1]
z1.values('y')[:] = [n[1] for n in nodes1]
z1.values('z')[:] = [n[2] for n in nodes1]
z1.values('s')[:] = scalar_data1

# Set face neighbors
z0.facemap.set_mapping(faces0, elements0, boundary_elems0, boundary_zones0)
z1.facemap.set_mapping(faces1, elements1, boundary_elems1, boundary_zones1)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('polygons2.dat')


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
plot.view.width = 2
plot.view.psi = 80
plot.view.theta = 30
plot.view.alpha = 0
plot.view.position = (-4.2, -8.0, 2.3)

# Showing mesh, we can see all the individual triangles
plot.show_mesh = True
fmaps.mesh.line_pattern = LinePattern.Dashed

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('polygons2.png', 600, supersample=3)

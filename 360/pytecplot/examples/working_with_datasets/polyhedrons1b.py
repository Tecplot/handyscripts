"""Polyhedral Finite-element Data Creation (Part 1b)

This script shows an alternative way to specify the connectivity for the same
polyhedron zone from Part 1. Two tetrahedrons are created by defining the node
locations and then the faces for each element. The element mapping is a list
of elements containing a list of faces containing a list of nodes for each
face.

Unlike the example in Part 1, the order of the nodes in each face does not
matter. This may simplify the assignment of complex polyhedral elements.

Again, the scalar data provided is cell-centered which must be specified when
the zone is created. In this case, :math:`(x, y, z)` positions are nodal, and
the scalar variable :math:`s` is cell-centered.

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

# Locations (x,y,z) of the nodes
nodes = ((0, 0, 0),
         (1, 1, 0),
         (1, 0, 1),
         (0, 1, 1),
         (0, 0, 1))

# node indices for each face of each element
elementmap = (((0, 1, 2),  # element 0
               (0, 1, 3),
               (1, 3, 2),
               (0, 2, 3)),
              ((0, 2, 3),  # element 1
               (2, 3, 4),
               (0, 2, 4),
               (0, 4, 3)))

# Calculate the number of unique faces
# (edges of the triangles) from the elementmap
num_faces = len(set( f for e in elementmap for f in e ))

# Scalar value at the cell centers
scalar_data = (0, 1)

# Setup dataset and zone
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])

# nodal locations for (x,y,z), cell-centered for the scalar s
locs = [ValueLocation.Nodal]*3 + [ValueLocation.CellCentered]

z = ds.add_poly_zone(ZoneType.FEPolyhedron,
                     name='FE Polyhedron Float (5,2,7) Cell Center',
                     locations=locs,
                     num_points=len(nodes),
                     num_elements=len(elementmap),
                     num_faces=num_faces)

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set facemap
z.facemap.set_elementmap(elementmap)

# Set the scalar data
z.values('s')[:] = scalar_data

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('polyhedrons1b.dat')


### Now we setup a nice view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

for ax in plot.axes:
    ax.show = True

plot.show_mesh = True
plot.show_contour = True
plot.show_scatter = True
plot.use_translucency = True
plot.use_lighting_effect = False

fmap = plot.fieldmap(z)
fmap.contour.contour_type = ContourType.PrimaryValue
fmap.scatter.symbol().shape = GeomShape.Sphere
fmap.scatter.color = plot.contour(0)
fmap.points.points_to_plot = PointsToPlot.AllCellCenters
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
fmap.effects.surface_translucency = 65

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10.1
plot.view.width = 2.15
plot.view.psi = 65
plot.view.theta = -39
plot.view.alpha = 0
plot.view.position = (6.35, -6.52, 4.80)

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('polyhedrons1b.png', 600, supersample=3)

r"""Polygonal Finite-element Data Creation (Part 1)

This script creates a quad of two triangles from scratch using the PyTecplot
low-level data creation interface. The dataset created is exacly the same as in
the "Triangle Finite-element Data Creation (Part 1)" example, however here we
use the polygonal data structure. The general steps are:

1. Setup the data
2. Create the tecplot dataset and variables
3. Create the zone
4. Set the node locations and connectivity lists
5. Set the (scalar) data
6. Write out data file
7. Adjust plot style and export image

The data created looks like this::

    Node positions (x,y,z):

                   (1,1,1)
                  3
                 / \
                /   \
     (0,1,.5)  2-----1  (1,0,.5)
                \   /
                 \ /
                  0
                   (0,0,0)

Element indices are used when identifying the left and right of each face,
where :math:`-1` is used to indicate no element::

                  *
              -1 / \ -1
                / 1 \
               *-----*
                \ 0 /
              -1 \ / -1
                  *

The nodes are created as a list of :math:`(x, y, z)` positions::

    [(x0, y0, z0), (x1, y1, z1)...]

which are transposed to lists of :math:`x`, :math:`y` and :math:`z`-positions::

    [(x0, x1, x2...), (y0, y1, y2...)...]

and passed to the :math:`(x, y, z)` arrays. The nodemap, or connectivity list,
is given as a list of lists which indicate the nodes used for each element. The
order of the node locations determines the indices used when specifying the
connectivity list.

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
nodes = ((0, 0, 0  ),
         (1, 0, 0.5),
         (0, 1, 0.5),
         (1, 1, 1  ))

# Faces (lines for polygons)
faces = ((0, 1),
         (1, 2),
         (2, 0),
         (1, 3),
         (3, 2))

# Elements (left, right) of each face
elements = (( 0, 0,  0,  1,  1),  # left elements
            (-1, 1, -1, -1, -1))  # right elements
num_elements = 2

# Scalar value at the nodes
scalar_data = (0, 1, 2, 3)

# Setup dataset and zone
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_poly_zone(ZoneType.FEPolygon, name='FE Polygon Float (4,2,5) Nodal',
                     num_points=len(nodes),
                     num_elements=num_elements,
                     num_faces=len(faces))

# Fill in node locations
z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]

# Set facemap
z.facemap.set_mapping(faces, elements)

# Set the scalar data
z.values('s')[:] = scalar_data

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('polygons1.dat')


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

tp.export.save_png('polygons1.png', 600, supersample=3)

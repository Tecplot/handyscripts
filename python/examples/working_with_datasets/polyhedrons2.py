"""Polyhedral Finite-element Data Creation (Part 2)

This script creates two tetrahedrons just as in Part 1, however they are
placed into two different zones. Boundary connections are then made to stitch
the two together.

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

# Tetrahedron in the first zone
nodes0 = ((0, 0, 0),
          (1, 1, 0),
          (1, 0, 1),
          (0, 1, 1))
faces0 = ((0, 1, 2),
          (0, 1, 3),
          (1, 3, 2),
          (0, 2, 3))
elems0 = (( 0,  0,  0,  0),
          (-1, -1, -1, -2))
scalar_data0 = (0,)
num_elements0 = 1

# One boundary element neighboring the
# first element (index 0)
# of the second zone (index 1)
boundary_elems0 = ((0,),)
boundary_zones0 = ((1,),)

# Tetrahedron in the second zone
nodes1 = ((0, 0, 0),
          (1, 0, 1),
          (0, 1, 1),
          (0, 0, 1))
faces1 = ((0, 1, 2),
          (0, 1, 3),
          (1, 3, 2),
          (0, 2, 3))
elems1 = (( 0,  0,  0,  0),
          (-2, -1, -1, -1))
scalar_data1 = (1,)
num_elements1 = 1

# One boundary element neighboring the
# first element (index 0)
# of the first zone (index 0)
boundary_elems1 = ((0,),)
boundary_zones1 = ((0,),)

# Setup dataset and zone
# Make sure to set the connectivity before any plot or style change.
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])

# nodal locations for (x,y,z), cell-centered for the scalar s
locs = [ValueLocation.Nodal]*3 + [ValueLocation.CellCentered]

z0 = ds.add_poly_zone(ZoneType.FEPolyhedron,
                      name='0: FE Polyhedron Float (4,1,4) Cell Center',
                      locations=locs,
                      num_points=len(nodes0),
                      num_elements=num_elements0,
                      num_faces=len(faces0))
z1 = ds.add_poly_zone(ZoneType.FEPolyhedron,
                      name='1: FE Polyhedron Float (4,1,4) Cell Center',
                      locations=locs,
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
z0.facemap.set_mapping(faces0, elems0, boundary_elems0, boundary_zones0)
z1.facemap.set_mapping(faces1, elems1, boundary_elems1, boundary_zones1)

# Write data out in tecplot text format
tp.data.save_tecplot_ascii('polyhedrons2.dat')


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

fmaps = plot.fieldmaps()
fmaps.contour.contour_type = ContourType.PrimaryValue
fmaps.scatter.symbol().shape = GeomShape.Sphere
fmaps.scatter.color = plot.contour(0)
fmaps.points.points_to_plot = PointsToPlot.AllCellCenters
fmaps.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
fmaps.effects.surface_translucency = 65

# View parameters obtained interactively from Tecplot 360
plot.view.distance = 10.1
plot.view.width = 2.15
plot.view.psi = 65
plot.view.theta = -39
plot.view.alpha = 0
plot.view.position = (6.35, -6.52, 4.80)

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('polyhedrons2.png', 600, supersample=3)

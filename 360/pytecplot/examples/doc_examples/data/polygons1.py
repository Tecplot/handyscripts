import tecplot as tp
from tecplot.constant import *

nodes = ((0, 0, 0  ),
         (1, 0, 0.5),
         (0, 1, 0.5),
         (1, 1, 1  ))
faces = ((0, 1),
         (1, 2),
         (2, 0),
         (1, 3),
         (3, 2))
elements = (( 0, 0,  0,  1,  1),  # elements to the left of each face
            (-1, 1, -1, -1, -1))  # elements to the right of each face
num_elements = 2
scalar_data = (0, 1, 2, 3)

ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
z = ds.add_poly_zone(ZoneType.FEPolygon,
                     name='FE Polygon Float (4,2,5) Nodal',
                     num_points=len(nodes),
                     num_elements=num_elements,
                     num_faces=len(faces))

z.values('x')[:] = [n[0] for n in nodes]
z.values('y')[:] = [n[1] for n in nodes]
z.values('z')[:] = [n[2] for n in nodes]
#{DOC:highlight}[
z.facemap.set_mapping(faces, elements)
#]
z.values('s')[:] = scalar_data

### setup a view of the data
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

cont = plot.contour(0)
cont.colormap_name = 'Sequential - Yellow/Green/Blue'
cont.colormap_filter.distribution = ColorMapDistribution.Continuous

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

# Turning on mesh, we can see all the individual triangles
plot.show_mesh = True
plot.fieldmap(z).mesh.line_pattern = LinePattern.Dashed

cont.levels.reset_to_nice()
tp.export.save_png('polygons1.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, SurfacesToPlot, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Pyramid.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian3D)

fmaps = plot.fieldmaps()
fmaps.contour.show = True
fmaps.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_contour = True
plot.contour(0).legend.show = False

for axis in plot.axes:
    axis.show = True

#{DOC:highlight}[
grid_area = plot.axes.grid_area
grid_area.fill_color = Color.SkyBlue
grid_area.show_border = True
grid_area.use_lighting_effect = True
#]

plot.view.fit()

tp.export.save_png('grid_area_3d.png', 600, supersample=3)

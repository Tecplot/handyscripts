from os import path
import tecplot as tp
from tecplot.constant import PlotType, SurfacesToPlot, Color, AxisTitleMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.show_contour = True
plot.contour(0).variable = dataset.variable('S')
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).legend.show = False

plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

xaxis = plot.axes.x_axis
xaxis.show = True
#{DOC:highlight}[
xaxis.title.title_mode = AxisTitleMode.UseText
xaxis.title.text = 'Longitudinal (m)'
xaxis.title.color = Color.BluePurple
xaxis.title.position = 10
#]

yaxis = plot.axes.y_axis
yaxis.show = True
#{DOC:highlight}[
yaxis.title.title_mode = AxisTitleMode.UseText
yaxis.title.text = 'Transverse (m)'
yaxis.title.color = Color.BluePurple
yaxis.title.position = 90
#]

zaxis = plot.axes.z_axis
zaxis.show = True
#{DOC:highlight}[
zaxis.title.title_mode = AxisTitleMode.UseText
zaxis.title.text = 'Height (m)'
zaxis.title.color = Color.BluePurple
zaxis.title.offset = 13
#]

plot.view.fit()

tp.export.save_png('axis_title_3d.png', 600, supersample=3)

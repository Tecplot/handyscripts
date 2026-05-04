from os import path
import tecplot as tp
from tecplot.constant import PlotType, SurfacesToPlot, Color, AxisTitleMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

plot = tp.active_frame().plot(PlotType.Cartesian2D)
plot.activate()

plot.show_contour = True
plot.contour(0).variable = dataset.variable('S')
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
plot.contour(0).legend.show = False

plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

xaxis = plot.axes.x_axis
#{DOC:highlight}[
xaxis.title.title_mode = AxisTitleMode.UseText
xaxis.title.text = 'Longitudinal (m)'
xaxis.title.color = Color.Blue
#]

# place the x-axis title at the x-coordinate 10.0
#{DOC:highlight}[
xaxis.title.position = 100 * (10.0 - xaxis.min) / (xaxis.max - xaxis.min)
#]

yaxis = plot.axes.y_axis
#{DOC:highlight}[
yaxis.title.title_mode = AxisTitleMode.UseText
yaxis.title.text = 'Transverse (m)'
yaxis.title.color = Color.Blue
#]

# place the y-axis title at the y-coordinate 0.0
#{DOC:highlight}[
yaxis.title.position = 100 * (0.0 - yaxis.min) / (yaxis.max - yaxis.min)
#]

tp.export.save_png('axis_title_2d.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType, PointsToPlot

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

# Enable 3D field plot and turn on contouring
frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()
plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')
plot.show_vector = True

#{DOC:highlight}[
points = plot.fieldmaps().points
points.points_to_plot = PointsToPlot.SurfaceCellCenters
points.step = (2,2)
#]

# save image to file
tp.export.save_png('fieldmap_points.png', 600, supersample=3)

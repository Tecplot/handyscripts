from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
#{DOC:highlight}[
plot = frame.plot(PlotType.Cartesian2D)
plot.activate()

plot.vector.u_variable = dataset.variable('U(M/S)')
plot.vector.v_variable = dataset.variable('V(M/S)')

plot.contour(2).variable = dataset.variable('T(K)')
plot.contour(2).colormap_name = 'Sequential - Yellow/Green/Blue'
#]

for z in dataset.zones():
    fmap = plot.fieldmap(z)
    fmap.contour.flood_contour_group = plot.contour(2)

#{DOC:highlight}[
plot.show_contour = True
plot.show_vector = True
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(2).levels.reset_to_nice()

# save image to file
tp.export.save_png('plot_field2d.png', 600, supersample=3)

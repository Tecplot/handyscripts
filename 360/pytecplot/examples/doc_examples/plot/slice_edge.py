from os import path
import tecplot as tp

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.show_slices = True
plot.contour(0).variable = dataset.variable('U(M/S)')

slice_0 = plot.slice(0)
#{DOC:highlight}[
slice_0.edge.show = True
slice_0.edge.line_thickness = 0.8
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('slice_edge.png', 600, supersample=3)

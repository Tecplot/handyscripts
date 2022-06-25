from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()
plot.show_contour = True
plot.use_translucency = True
plot.contour(0).variable = dataset.variable('S')

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

# save image to file
tp.export.save_png('plot_field.png', 600, supersample=3)

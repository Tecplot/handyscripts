from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = True
plot.contour(0).variable = dataset.variable('P(N)')
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

#{DOC:highlight}[
plot.view.fit_to_nice()
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('view_2D.png', 600, supersample=3)

from os import path
import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'SpaceShip.lpk')
dataset = tp.load_layout(infile)

frame = tp.active_frame()
#{DOC:highlight}[
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()
plot.use_lighting_effect = False
plot.show_streamtraces = False
plot.use_translucency = True
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

# save image to file
tp.export.save_png('plot_field3d.png', 600, supersample=3)

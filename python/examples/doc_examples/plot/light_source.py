from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

#{DOC:highlight}[
plot.light_source.direction = (0., -0.7, 0.9)
plot.light_source.intensity = 70
plot.light_source.specular_intensity = 80
plot.light_source.specular_shininess = 50
#]

tp.export.save_png('light_source.png')


from os import path
import tecplot as tp
from tecplot.constant import Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'Pyramid.plt')
dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.show_slices = True
#{DOC:highlight}[
plot.slice(0).contour.show = False
shade = plot.slice(0).shade
shade.show = True
shade.color = Color.Red  # Slice will be colored solid red.
#]
tp.export.save_png('slice_shade.png', 600, supersample=3)

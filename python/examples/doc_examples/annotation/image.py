import os

import tecplot as tp
from tecplot.constant import PlotType

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(datafile)

frame = tp.active_frame()

plot2d = frame.plot(PlotType.Cartesian2D)
plot2d.activate()
plot2d.show_contour = True
plot2d.contour(0).colormap_name = 'Sequential - Blue'
plot2d.contour(0).variable = dataset.variable('S')
tp.export.save_png('embedded_image.png')

plot3d = frame.plot(PlotType.Cartesian3D)
plot3d.activate()
plot3d.show_contour = True
#{DOC:highlight}[
frame.add_image('embedded_image.png', (5, 55), 40)
#]

tp.export.save_png('image.png')

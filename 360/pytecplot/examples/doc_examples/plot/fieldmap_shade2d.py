import os
import random
import tecplot
from tecplot.constant import Color, PlotType

random.seed(1)

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tecplot.data.load_tecplot(datafile)
frame = dataset.frame
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()

for zone in dataset.zones():
    color = Color(random.randint(0,63))
    while color == Color.White:
        color = Color(random.randint(0,63))
#{DOC:highlight}[
    plot.fieldmap(zone).shade.color = color
#]

tecplot.export.save_png('fieldmap_shade2d.png', 600, supersample=3)

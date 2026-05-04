from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()
plot.contour(0).variable = dataset.variable('T(K)')
plot.show_scatter = True

#{DOC:highlight}[
plot.scatter.variable = dataset.variable('P(N)')
#]

for z in dataset.zones():
    scatter = plot.fieldmap(z).scatter
    scatter.symbol_type = SymbolType.Geometry
    scatter.symbol().shape = GeomShape.Circle
    scatter.fill_mode = FillMode.UseSpecificColor
    scatter.fill_color = plot.contour(0)
    scatter.color = plot.contour(0)
    scatter.size_by_variable = True

frame.add_text('Size of dots indicate relative pressure', (20, 80))

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('scatter.png')

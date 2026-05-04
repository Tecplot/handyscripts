from os import path
import tecplot as tp
from tecplot.constant import PlotType, SymbolType, FillMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()
plot.show_scatter = True

#{DOC:highlight}[
scatter = plot.fieldmaps().scatter
scatter.symbol_type = SymbolType.Geometry
scatter.fill_mode = FillMode.UseSpecificColor
scatter.fill_color = plot.contour(0)
scatter.size = 1
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('fieldmap_scatter.png', 600, supersample=3)

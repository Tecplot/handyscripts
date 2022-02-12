from os import path
import tecplot as tp
from tecplot.constant import (Color, PlotType, PointsToPlot, SymbolType,
                                  GeomShape, FillMode)

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian2D
plot = frame.plot()
plot.show_shade = True
#{DOC:highlight}[
plot.show_scatter = True
#]

# get handle to a collection of all fieldmaps
fmaps = plot.fieldmaps()

fmaps.points.points_to_plot = PointsToPlot.SurfaceCellCenters
fmaps.points.step = (4,4)
fmaps.shade.color = Color.LightBlue

#{DOC:highlight}[
fmaps.scatter.fill_mode = FillMode.UseSpecificColor
fmaps.scatter.fill_color = Color.Yellow
fmaps.scatter.size = 3
fmaps.scatter.symbol_type = SymbolType.Text
#]

for i, fmap in enumerate(fmaps):
#{DOC:highlight}[
    fmap.scatter.color = Color((i % 4) + 13)
    fmap.scatter.symbol().text = hex(i)[-1]
#]

tp.export.save_png('fieldmap_scatter_text.png', 600, supersample=3)

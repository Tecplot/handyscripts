from os import path
import tecplot as tp
from tecplot.constant import (PlotType, Color, GeomShape, SymbolType,
                              FillMode)

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()
plot.show_symbols = True

cols = [Color.DeepRed, Color.Blue, Color.Fern]
shapes = [GeomShape.Square, GeomShape.Circle, GeomShape.Del]

lmaps = plot.linemaps()

lmaps.show = True
lmaps.symbols.show = True
lmaps.symbols.size = 4.5
lmaps.symbols.fill_mode = FillMode.UseSpecificColor
#{DOC:highlight}[
lmaps.symbols.symbol_type = SymbolType.Geometry
#]

for lmap, color, shape in zip(lmaps, cols, shapes):
    lmap.line.color = color
    lmap.symbols.color = color
    lmap.symbols.fill_color = color
#{DOC:highlight}[
    lmap.symbols.symbol().shape = shape
#]

plot.view.fit()

# save image to file
tp.export.save_png('linemap_symbols_geometry.png', 600, supersample=3)

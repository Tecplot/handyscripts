from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, FillMode, GeomShape

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()
#{DOC:highlight}[
plot.show_symbols = True
#]

lmaps = plot.linemaps(0, 1, 2)

#{DOC:highlight}[
lmaps.symbols.show = True
lmaps.symbols.symbol().shape = GeomShape.Square
lmaps.symbols.size = 2.5
lmaps.symbols.color = Color.Blue
lmaps.symbols.line_thickness = 0.4
lmaps.symbols.fill_mode = FillMode.UseSpecificColor
lmaps.symbols.fill_color = Color.Azure
#]

# save image to file
tp.export.save_png('linemap_symbols.png', 600, supersample=3)

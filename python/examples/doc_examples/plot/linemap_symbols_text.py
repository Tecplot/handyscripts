from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, SymbolType, FillMode

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()
plot.show_symbols = True

cols = [Color.DeepRed, Color.Blue, Color.Fern]
chars = ['S','D','M']

lmaps = plot.linemaps()
lmaps.show = True
lmaps.symbols.show = True
lmaps.symbols.size = 2.5
lmaps.symbols.color = Color.White
lmaps.symbols.fill_mode = FillMode.UseSpecificColor
#{DOC:highlight}[
lmaps.symbols.symbol_type = SymbolType.Text
#]

for lmap, color, character in zip(lmaps, cols, chars):
    lmap.line.color = color
    lmap.symbols.fill_color = color
#{DOC:highlight}[
    lmap.symbols.symbol().text = character
#]

plot.view.fit()

# save image to file
tp.export.save_png('linemap_symbols_text.png', 600, supersample=3)

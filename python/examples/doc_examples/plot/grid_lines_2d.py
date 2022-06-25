from os import path
import tecplot as tp
from tecplot.constant import LinePattern, Color

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
dataset = tp.load_layout(datafile)

for axis in tp.active_frame().plot().axes:
#{DOC:highlight}[
    grid_lines = axis.grid_lines
    grid_lines.show = True
    grid_lines.line_pattern = LinePattern.LongDash
    grid_lines.color = Color.Green
#]

tp.export.save_png('grid_lines_2d.png', 600, supersample=3)

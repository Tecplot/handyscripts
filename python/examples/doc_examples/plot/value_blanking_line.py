from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()

lmap = plot.linemap(0)

line = lmap.line
line.color = Color.Blue
line.line_thickness = 1
line.line_pattern = LinePattern.LongDash
line.pattern_length = 2

#{DOC:highlight}[
plot.value_blanking.active = True
constraint = plot.value_blanking.constraint(0)
constraint.active = True
constraint.compare_by = ConstraintOp2Mode.UseConstant
constraint.comparison_operator = RelOp.LessThanOrEqual
constraint.comparison_value = 6
constraint.variable = dataset.variable('Month')
#]

tp.export.save_png('value_blanking_line.png', 600)

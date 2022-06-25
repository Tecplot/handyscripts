from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)

plot.show_contour = True

#{DOC:highlight}[
plot.value_blanking.active = True
plot.value_blanking.cell_mode = ValueBlankCellMode.AnyCorner
constraint = plot.value_blanking.constraint(0)
constraint.active = True
constraint.compare_by = ConstraintOp2Mode.UseConstant
constraint.comparison_operator = RelOp.LessThanOrEqual
constraint.comparison_value = 5
constraint.variable = dataset.variable('X(M)')
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('value_blanking_2d.png', 600)

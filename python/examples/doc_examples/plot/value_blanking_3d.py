from os import path
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
tp.load_layout(infile)

frame = tp.active_frame()
plot = frame.plot()

#{DOC:highlight}[
plot.value_blanking.active = True
plot.value_blanking.cell_mode = ValueBlankCellMode.AnyCorner
constraint = plot.value_blanking.constraint(0)
constraint.active = True
constraint.compare_by = ConstraintOp2Mode.UseConstant
constraint.comparison_operator = RelOp.GreaterThan
constraint.comparison_value = 0
constraint.variable = frame.dataset.variable('X')
#]

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('value_blanking_3d.png', 600)

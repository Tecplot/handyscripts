import numpy as np
import tecplot as tp
from tecplot.data.operate import execute_equation
from tecplot.constant import (PlotType, PointsToPlot, VectorType,
                              ArrowheadStyle)

frame = tp.active_frame()
dataset = frame.dataset
for v in ['X','Y','Z','P','Q','R']:
    dataset.add_variable(v)
zone = dataset.add_ordered_zone('Zone', (30,30,30))
xx = np.linspace(0,30,30)
for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
    zone.values(v)[:] = arr.ravel()
execute_equation('{P} = -10 * {X}    +      {Y}**2 + {Z}**2')
execute_equation('{Q} =       {X}    - 10 * {Y}    - {Z}**2')
execute_equation('{R} =       {X}**2 +      {Y}**2 - {Z}   ')

frame.plot_type = PlotType.Cartesian3D
plot = frame.plot()
plot.contour(0).variable = dataset.variable('P')
plot.contour(0).colormap_name = 'Two Color'
plot.contour(0).levels.reset_to_nice()
#{DOC:highlight}[
plot.vector.u_variable = dataset.variable('P')
plot.vector.v_variable = dataset.variable('Q')
plot.vector.w_variable = dataset.variable('R')
#]
plot.show_vector = True

points = plot.fieldmap(0).points
points.points_to_plot = PointsToPlot.AllNodes
points.step = (5,3,2)

#{DOC:highlight}[
vector = plot.fieldmap(0).vector
vector.show = True
vector.vector_type = VectorType.MidAtPoint
vector.arrowhead_style = ArrowheadStyle.Filled
vector.color = plot.contour(0)
#]
vector.line_thickness = 0.4

# save image to file
tp.export.save_png('fieldmap_vector.png', 600, supersample=3)

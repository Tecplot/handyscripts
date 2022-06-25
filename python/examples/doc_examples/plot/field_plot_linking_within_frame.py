import os
import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
tp.load_layout(infile)

dataset = tp.active_frame().dataset
frame = tp.active_frame()
plot = frame.plot()

#{DOC:highlight}[
frame_linking = plot.linking_within_frame
frame_linking.link_gridline_style = True
frame_linking.link_axis_style = True
#]

plot.axes.grid_area.fill_color = Color.Mahogany
plot.axes.grid_area.use_lighting_effect = False

#{DOC:highlight}[
# With linked axis style, we only need to modify
# one axis and all others will get the same.
#]
axis = plot.axes.x_axis
axis.show = True
axis.grid_lines.line_thickness = 0.2
axis.title.color = Color.Green
axis.ticks.show_on_opposite_edge = True
axis.minor_grid_lines.show = True
axis.minor_grid_lines.line_pattern = LinePattern.Dotted
axis.minor_grid_lines.color = Color.Cyan
axis.line.line_thickness = 0.2

plot.view.fit()

tp.export.save_png('field_plot_link_within_frame.png')

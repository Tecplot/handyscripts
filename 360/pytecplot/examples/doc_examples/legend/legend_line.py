import os

import tecplot
from tecplot.constant import *

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
plot = frame.plot()
frame.plot_type = tecplot.constant.PlotType.XYLine

for i in range(3):
    plot.linemap(i).show = True
    plot.linemap(i).line.line_thickness = .4

y_axis = plot.axes.y_axis(0)
y_axis.title.title_mode = AxisTitleMode.UseText
y_axis.title.text = 'Rainfall (in)'
y_axis.fit_range_to_nice()

#{DOC:highlight}[
legend = plot.legend
legend.show = True
legend.box.box_type = TextBox.Filled
legend.box.color = Color.Purple
legend.box.fill_color = Color.LightGrey
legend.box.line_thickness = .4
legend.box.margin = 5

legend.anchor_alignment = AnchorAlignment.MiddleRight
legend.row_spacing = 1.5
legend.show_text = True
legend.font.typeface = 'Arial'
legend.font.italic = True

legend.text_color = Color.Black
legend.position = (90, 88)
#]

tecplot.export.save_png('legend_line.png', 600, supersample=3)

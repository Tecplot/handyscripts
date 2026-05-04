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
#{DOC:highlight}[
plot.view.fit_to_nice()
#]

tecplot.export.save_png('view_line.png', 600, supersample=3)

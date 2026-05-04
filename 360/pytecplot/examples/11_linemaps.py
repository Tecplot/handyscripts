from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, LinePattern, AxisTitleMode

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# load data from examples directory
examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)

# get handle to the active frame and set plot type to XY Line
frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()

# We will set the name, color and a few other properties
# for the first three linemaps in the dataset.
names = ['Seattle', 'Dallas', 'Miami']
colors = [Color.Blue, Color.DeepRed, Color.Khaki]

# loop over the linemaps, setting style for each
for lmap,name,color in zip(plot.linemaps(),names,colors):
    lmap.show = True
    lmap.name = name # This will be used in the legend

    # Changing some line attributes
    line = lmap.line
    line.color = color
    line.line_thickness = 1
    line.line_pattern = LinePattern.LongDash
    line.pattern_length = 2

# Set the y-axis label
plot.axes.y_axis(0).title.title_mode = AxisTitleMode.UseText
plot.axes.y_axis(0).title.text = 'Rainfall'

# Turn on legend
plot.legend.show = True

# Adjust the axes limits to show all the data
plot.view.fit()

# save image to file
tp.export.save_png('linemap.png', 600, supersample=3)

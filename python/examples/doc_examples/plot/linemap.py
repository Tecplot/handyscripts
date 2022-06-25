from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, LinePattern, AxisTitleMode

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

lmaps = plot.linemaps()

# set common style for all linemaps in the collection
#{DOC:highlight}[
lmaps.show = True
lmaps.line.line_thickness = 1
lmaps.line.line_pattern = LinePattern.LongDash
lmaps.line.pattern_length = 2
#]

# loop over the linemaps, setting name and color for each
#{DOC:highlight}[
for lmap, name, color in zip(lmaps, names, colors):
    lmap.name = name
    lmap.line.color = color
#]

# Set the y-axis label
plot.axes.y_axis(0).title.title_mode = AxisTitleMode.UseText
plot.axes.y_axis(0).title.text = 'Rainfall'

# Turn on legend
plot.legend.show = True

# Adjust the axes limits to show all the data
plot.view.fit()

# save image to file
tp.export.save_png('linemap.png', 600, supersample=3)

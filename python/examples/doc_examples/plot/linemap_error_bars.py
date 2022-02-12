from math import sqrt
from os import path
import tecplot as tp
from tecplot.constant import PlotType, Color, ErrorBar

# setup dataset
frame = tp.active_frame()
ds = frame.create_dataset('Dataset')
for v in ['x', 'y', 'xerr', 'yerr']:
    ds.add_variable(v)
zone = ds.add_ordered_zone('Zone', 5)

# create some data (x, y)
zone.values('x')[:] = [0,1,2,3,4]
zone.values('y')[:] = [1,2,4,8,10]

# error in x is a constant
zone.values('xerr')[:] = [0.2]*5

# error in y is the square-root of the value
zone.values('yerr')[:] = [sqrt(y) for y in zone.values('y')[:]]

frame.plot_type = PlotType.XYLine
plot = frame.plot()

plot.delete_linemaps()
xerr_lmap = plot.add_linemap('xerr', zone, ds.variable('x'),
                             ds.variable('y'))
yerr_lmap = plot.add_linemap('yerr', zone, ds.variable('x'),
                             ds.variable('y'))

#{DOC:highlight}[
xerr_lmap.error_bars.variable = ds.variable('xerr')
xerr_lmap.error_bars.bar_type = ErrorBar.Horz
xerr_lmap.error_bars.color = Color.Blue
xerr_lmap.error_bars.line_thickness = 0.8
xerr_lmap.error_bars.show = True

yerr_lmap.error_bars.variable = ds.variable('yerr')
yerr_lmap.error_bars.bar_type = ErrorBar.Vert
yerr_lmap.error_bars.color = Color.Blue
yerr_lmap.error_bars.line_thickness = 0.8
yerr_lmap.error_bars.show = True
#]

plot.show_lines = False
#{DOC:highlight}[
plot.show_error_bars = True
#]

plot.view.fit()

tp.export.save_png('linemap_error_bars.png', 600, supersample=3)

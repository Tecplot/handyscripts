import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, Color, AxisTitleMode

npoints = 300
r = np.linspace(0, 2000, npoints)
theta = np.linspace(0, 1000, npoints)

frame = tp.active_frame()
dataset = frame.create_dataset('Data', ['R', 'Theta'])
zone = dataset.add_ordered_zone('Zone', (300,))
zone.values('R')[:] = r
zone.values('Theta')[:] = theta

plot = frame.plot(PlotType.PolarLine)
plot.activate()

plot.axes.r_axis.max = np.max(r)

plot.delete_linemaps()
lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                        dataset.variable('Theta'))
lmap.line.line_thickness = 0.8

raxis = plot.axes.r_axis
raxis.line.show_both_directions = True
raxis.line.show_perpendicular = True

#{DOC:highlight}[
raxis.title.title_mode = AxisTitleMode.UseText
raxis.title.text = 'Radial Position (cm)'
raxis.title.show_on_all_radial_axes = True
raxis.title.color = Color.Blue
raxis.title.position = 80
#]

plot.view.fit()

tp.export.save_png('axis_title_radial.png', 600, supersample=3)

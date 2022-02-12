import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode

npoints = 300
r = np.linspace(0, 2000, npoints)
theta = np.linspace(0, 10, npoints)

frame = tp.active_frame()
dataset = frame.create_dataset('Data', ['R', 'Theta'])
zone = dataset.add_ordered_zone('Zone', (300,))
zone.values('R')[:] = r
zone.values('Theta')[:] = theta
plot = frame.plot(PlotType.PolarLine)
plot.activate()

plot.delete_linemaps()
lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                        dataset.variable('Theta'))
lmap.line.line_thickness = 0.8

r_axis = plot.axes.r_axis
r_axis.max = np.max(r)
r_axis.tick_labels.angle = 45
r_axis.tick_labels.font.size *= 2

theta_axis = plot.axes.theta_axis
theta_axis.mode = ThetaMode.Radians
theta_axis.tick_labels.font.size *= 2

plot.view.fit()

tp.export.save_png('axis_line_2d.png', 600, supersample=3)

import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode

frame = tp.active_frame()

npoints = 300
r = np.linspace(0, 2000, npoints)
theta = np.linspace(0, 10, npoints)

dataset = frame.create_dataset('Data', ['R', 'Theta'])
zone = dataset.add_ordered_zone('Zone', (300,))
zone.values('R')[:] = r
zone.values('Theta')[:] = theta

plot = frame.plot(PlotType.PolarLine)
plot.activate()

#{DOC:highlight}[
plot.axes.r_axis.max = np.max(r)
plot.axes.theta_axis.mode = ThetaMode.Radians
#]

plot.delete_linemaps()
lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                        dataset.variable('Theta'))
lmap.line.line_thickness = 0.8

plot.view.fit()

tp.export.save_png('axes_polar.png', 600, supersample=3)

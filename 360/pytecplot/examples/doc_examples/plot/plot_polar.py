import numpy as np
import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

npoints = 300
r = np.linspace(0, 2000, npoints)
theta = np.linspace(0, 10, npoints)

dataset = frame.create_dataset('Data', ['R', 'Theta'])
zone = dataset.add_ordered_zone('Zone', (300,))
zone.values('R')[:] = r
zone.values('Theta')[:] = theta

#{DOC:highlight}[
plot = frame.plot(PlotType.PolarLine)
plot.activate()
plot.axes.r_axis.max = r.max()
plot.axes.theta_axis.mode = ThetaMode.Radians
plot.delete_linemaps()
lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                            dataset.variable('Theta'))
#]
lmap.line.line_thickness = 0.8
lmap.line.color = Color.Green

plot.view.fit()

tp.export.save_png('plot_polar.png', 600, supersample=3)

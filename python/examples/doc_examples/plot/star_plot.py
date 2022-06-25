import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, ThetaMode, NumberFormat, AxisAlignment

np.random.seed(2)
npoints = 7
theta = np.linspace(0, npoints, npoints+1)

frame = tp.active_frame()
dataset = frame.create_dataset('Data', ['Magnitude', 'Property'])

for i in range(3):
    r = list(np.random.uniform(0.01, 0.99, npoints))
    r.append(r[0])
    zone = dataset.add_ordered_zone('Zone {}'.format(i), (npoints+1,))
    zone.values('Magnitude')[:] = r
    zone.values('Property')[:] = theta

plot = frame.plot(PlotType.PolarLine)
plot.activate()
plot.delete_linemaps()

for i, zone in enumerate(dataset.zones()):
    lmap = plot.add_linemap('Linemap {}'.format(i), zone,
                            dataset.variable('Magnitude'),
                            dataset.variable('Property'))
    lmap.line.line_thickness = 0.8

r_axis = plot.axes.r_axis
r_axis.max = 1
r_axis.line.show = False
r_axis.title.position = 85
r_axis.line.alignment = AxisAlignment.WithOpposingAxisValue
r_axis.line.opposing_axis_value = 1

theta_axis = plot.axes.theta_axis
theta_axis.origin = 1
theta_axis.mode = ThetaMode.Arbitrary
theta_axis.min = 0
theta_axis.max = theta.max()
theta_axis.period = npoints
theta_axis.ticks.auto_spacing = False
theta_axis.ticks.spacing = 1
theta_axis.ticks.minor_num_ticks = 0
theta_axis.title.show = False

theta_labels = theta_axis.tick_labels.format
theta_labels.format_type = NumberFormat.CustomLabel
theta_labels.add_custom_labels('A', 'B', 'C', 'D', 'E', 'F', 'G')
theta_labels.custom_labels_index = 0

plot.view.fit()

tp.export.save_png('star_plot.png', 600, supersample=3)

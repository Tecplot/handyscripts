import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, Color

frame = tp.active_frame()

npoints = 100
x = np.linspace(-10,10,npoints)
t = x**2
p = 0.1 * np.sin(x)

dataset = frame.create_dataset('data', ['Position (m)', 'Temperature (K)',
                                        'Pressure (Pa)'])
zone = dataset.add_ordered_zone('zone', (100,))
zone.values('Position (m)')[:] = x
zone.values('Temperature (K)')[:] = t
zone.values('Pressure (Pa)')[:] = p

plot = frame.plot(PlotType.XYLine)
plot.activate()
plot.delete_linemaps()

temp = plot.add_linemap('temp', zone, dataset.variable('Position (m)'),
                 dataset.variable('Temperature (K)'))
press = plot.add_linemap('press', zone, dataset.variable('Position (m)'),
                         dataset.variable('Pressure (Pa)'))

# Color the line and the y-axis for temperature
temp.line.color = Color.RedOrange
temp.line.line_thickness = 0.8

#{DOC:highlight}[
ax = plot.axes.y_axis(0)
#]
ax.line.color = temp.line.color
ax.tick_labels.color = temp.line.color
ax.title.color = temp.line.color

# set pressure linemap to second x-axis
press.y_axis_index = 1

# Color the line and the y-axis for pressure
press.line.color = Color.Chartreuse
press.line.line_thickness = 0.8

#{DOC:highlight}[
ax = plot.axes.y_axis(1)
#]
ax.line.color = press.line.color
ax.tick_labels.color = press.line.color
ax.title.color = press.line.color

tp.export.save_png('axes_line.png', 600, supersample=3)

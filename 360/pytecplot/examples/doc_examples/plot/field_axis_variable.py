import tecplot as tp
from tecplot.constant import PlotType

fr = tp.active_frame()
ds = fr.create_dataset('D', ['X', 'Y', 'Z', 'U', 'V'])
axes = fr.plot(PlotType.Cartesian3D).axes

# prints: ('X', 'Y')
print(axes.x_axis.variable.name, axes.y_axis.variable.name)

axes.x_axis.variable = ds.variable('U')
axes.y_axis.variable = ds.variable('V')

# prints: ('U', 'V)
print(axes.x_axis.variable.name, axes.y_axis.variable.name)

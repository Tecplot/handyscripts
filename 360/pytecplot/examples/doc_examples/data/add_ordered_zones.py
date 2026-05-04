import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, Color

# Generate data
x = np.linspace(-4, 4, 100)

# Setup Tecplot dataset
dataset = tp.active_frame().create_dataset('Data', ['x', 'y'])

# Create a zone
#{DOC:highlight}[
zone = dataset.add_ordered_zone('sin(x)', len(x))
#]
zone.values('x')[:] = x
zone.values('y')[:] = np.sin(x)

# Create another zone
#{DOC:highlight}[
zone = dataset.add_ordered_zone('cos(x)', len(x))
#]
zone.values('x')[:] = x
zone.values('y')[:] = np.cos(x)

# And one more zone
#{DOC:highlight}[
zone = dataset.add_ordered_zone('tan(x)', len(x))
#]
zone.values('x')[:] = x
zone.values('y')[:] = np.tan(x)

# Set plot type to XYLine
plot = tp.active_frame().plot(PlotType.XYLine)
plot.activate()

# Show all linemaps and make the lines a bit thicker
for lmap in plot.linemaps():
    lmap.show = True
    lmap.line.line_thickness = 0.6

plot.legend.show = True

tp.export.save_png('add_ordered_zones.png', 600, supersample=3)


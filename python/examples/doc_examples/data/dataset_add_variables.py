import math
import tecplot as tp
from tecplot.constant import PlotType

# Setup Tecplot dataset
dataset = tp.active_frame().create_dataset('Data')
#{DOC:highlight}[
dataset.add_variable('x')
dataset.add_variable('s')
#]
zone = dataset.add_ordered_zone('Zone', 100)

# Fill the dataset
x = [0.1 * i for i in range(100)]
zone.values('x')[:] = x
zone.values('s')[:] = [math.sin(i) for i in x]

# Set plot type to XYLine
tp.active_frame().plot(PlotType.XYLine).activate()

tp.export.save_png('add_variables.png', 600, supersample=3)

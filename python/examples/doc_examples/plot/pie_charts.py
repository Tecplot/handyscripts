import os
import numpy as np

import tecplot as tp
from tecplot.constant import *


def normalize_variable(dataset, varname, nsigma=2):
    '''
    Normalize a variable such that the specified number of standard deviations
    are within the range [0.5, 1] and the mean is transformed to 0.5. The
    new variable will append " normalized" to the original variable's name.
    '''
    with tp.session.suspend():
        newvarname = varname + ' normalized'
        dataset.add_variable(newvarname)
        data = np.concatenate([z.values(varname).as_numpy_array()
                               for z in dataset.zones()])
        vmin = data.mean() - nsigma * data.std()
        vmax = data.mean() + nsigma * data.std()
        for z in dataset.zones():
            arr = z.values(varname).as_numpy_array()
            z.values(newvarname)[:] = (arr - vmin) / (vmax - vmin)


examples_dir = tp.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
dataset = tp.data.load_tecplot(infile)

frame = tp.active_frame()
plot = frame.plot(PlotType.Cartesian2D)
plot.show_scatter = True

plot.axes.x_axis.min = 6
plot.axes.x_axis.max = 8
plot.axes.y_axis.min = 1.5
plot.axes.y_axis.max = 3.0

# Normalize variables to the range [0, 1]
normalize_variable(dataset, 'T(K)')
normalize_variable(dataset, 'P(N)')

frame.add_text(r'Normalized Temperature in Red', (50, 95), color=Color.Red)
frame.add_text(r'Normalized Pressure in Blue', (50, 92), color=Color.Blue)

#{DOC:highlight}[
fmaps = plot.fieldmaps()
fmaps.scatter.symbol().shape = GeomShape.PieChart
fmaps.scatter.size = 4.0

pie_charts = plot.scatter.pie_charts
pie_charts.wedge(0).show = True
pie_charts.wedge(0).show_label = False
pie_charts.wedge(0).variable = dataset.variable('T(K) normalized')
pie_charts.wedge(0).color = Color.Red

pie_charts.wedge(1).show = True
pie_charts.wedge(1).show_label = False
pie_charts.wedge(1).variable = dataset.variable('P(N) normalized')
pie_charts.wedge(1).color = Color.Blue
#]

tp.export.save_png('pie_charts.png')

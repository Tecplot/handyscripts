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
plot.show_contour = True

# Variables must be normalized relative to each other
# to make effective use of RGB coloring.
normalize_variable(dataset, 'T(K)')
normalize_variable(dataset, 'P(N)')

#{DOC:highlight}[
plot.rgb_coloring.mode = RGBMode.SpecifyGB

# all three channel variables must be set even if
# we are only contouring on two of them.
plot.rgb_coloring.red_variable = dataset.variable(0)
plot.rgb_coloring.green_variable = dataset.variable('P(N) normalized')
plot.rgb_coloring.blue_variable = dataset.variable('T(K) normalized')

plot.rgb_coloring.legend.show = True
plot.rgb_coloring.legend.use_variable_for_green_label = False
plot.rgb_coloring.legend.green_label = 'Pressure'
plot.rgb_coloring.legend.use_variable_for_blue_label = False
plot.rgb_coloring.legend.blue_label = 'Temperature'

plot.fieldmaps().contour.flood_contour_group = plot.rgb_coloring
#]

tp.export.save_png('rgb_coloring.png')

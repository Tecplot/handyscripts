import os

import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')

dataset = tp.data.load_tecplot(datafile)

plot = tp.active_frame().plot()
plot.show_contour = True

xax = plot.axes.x_axis
xax.min = -0.005
xax.max = 0.015
yax = plot.axes.y_axis
yax.min = -0.01
yax.max = 0.002

# Setup value blanking
vblank = plot.value_blanking
constraint = vblank.constraint(0)
constraint.variable_index = 1
constraint.comparison_operator = RelOp.GreaterThan
constraint.active = True
vblank.active = True

# Use list comprehension to get all zones assocaitated with
# a specific strand, in this case strand 1
in_zns = [zn for zn in dataset.zones() if zn.strand == 1]

# Extract all zones assocaitated with strand 1
ext_zns = tp.data.extract.extract_blanked_zones(in_zns)

# Place all extracted zones into the same strand
for zn in ext_zns:
    zn.strand = 2

# Turn off plotting for the original zone and turn on plotting
# of the extracted zones.
plot.fieldmap(0).show = False
plot.fieldmap(1).show = True

tp.export.save_time_animation_mpeg4('extract_blanked_zones.mp4',
                                    width=400, end_time=0.0004,
                                    supersample=3)

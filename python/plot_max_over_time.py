"""Plots the maximums for one zone through time

Description
-----------
This connected-mode script creates a line graph of the maximum values from a zone
over time, as seen in this Ask the Expert video (at ~6:00):
https://www.tecplot.com/2020/01/10/webinar-ask-the-expert-about-tecplot-360/

Usage:
    > python plot_max_over_time.py

For example data, see the link above, or the VortexShedding.plt file found in the 
examples directory in the Tecplot 360 installation folder.
"""

import tecplot as tp
from tecplot.constant import *
tp.session.connect() #connect to a live running instance of Tecplot 360

# Suspend the interface to speed up execution time
with tp.session.suspend():
    dataset = tp.active_frame().dataset
    values = []
    var_name = 'U(M/S)'
    for z in dataset.zones():
        values.append((z.solution_time, z.values(var_name).max()))

    # Create a new frame and stuff the extracted values into it for plotting
    new_frame = tp.active_page().add_frame()
    ds = new_frame.create_dataset('Max {} over time'.format(var_name), ['t',var_name])
    zone = ds.add_ordered_zone('Max {} over time'.format(var_name), len(values))
    zone.values('t')[:] = [v[0] for v in values]
    zone.values(var_name)[:] = [v[1] for v in values]
    new_frame.plot(PlotType.XYLine).activate()

"""Creates an IJ Ordered zone from a set of transient line zones.

usage:

    > python -O MakeIJZoneFromTransientLines.py

Necessary modules
-----------------
numpy
    A general-purpose array-processing package
    https://pypi.org/project/numpy/

Description
-----------
To run this script we must first have a set of transient lines which are all the
same dimension (see VerticalProfile.py). Enable PyTecplot Connections via the 
Scripting menu to connect to the running instance of Tecplot 360.

This script will connect to Tecplot 360, and prompt you for the strand that represents
the line zones. It will create a new variable called 'time', create an IJ zone and 
apply all solution variables to the new zone.

You will typically plot the resulting zone with 'time' on the X-Axis, depth/height on the
Y-Axis and color by a scalar variable.
"""
import numpy as np
import tecplot as tp
from tecplot.constant import ValueLocation
tp.session.connect()

strand = int(input("Which strand represents the lines?"))
dataset = tp.active_frame().dataset
zones = [z for z in dataset.zones() if z.strand == strand]

imax = zones[0].num_points
jmax = len(zones)

if __debug__:
    for z in zones:
        if z.num_points != imax:
            raise Exception("All line zones must have the same number of points!")

with tp.session.suspend():
    try:
        time_var = dataset.variable('time')
    except:
        time_var = dataset.add_variable('time')

    new_zone = dataset.add_ordered_zone("TransientLinesAsIJData", (imax,jmax,1),locations=[ValueLocation.Nodal]*dataset.num_variables)

    for z in zones:
        time_var.values(z)[:] = [z.solution_time]*imax

    for v in dataset.variables():
        print("Setting values for: {}".format(v.name))
        values = np.empty((jmax,imax))
        for j,z in enumerate(zones):
            values[j] = z.values(v).as_numpy_array()
        new_zone.values(v)[:] = values.ravel()

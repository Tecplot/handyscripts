'''Creating several zones and variables using the suspend context.

This example illustrates the effectiveness of the tp.session.suspend() context
manager - especially in connected mode. Outside this context, the Tecplot
engine (batch) or the Tecplot 360 GUI (connected) will always attempt to "keep
up" with changes made during, for example, data-loading-type operations.

When connected to a running Tecplot 360 through the PyTecplot Conections
feature, This script runs significantly faster when using the suspend
context. The difference in speed is less pronounced in batch though there
is still some speed up to be observed.
'''
import contextlib
import time

from numpy import random as rand

import tecplot as tp
from tecplot.constant import *

rand.seed(1)

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

    # clear current layout (clears data as well)
    tp.new_layout()

# Run this script with "-s" to invoke the suspend() context
@contextlib.contextmanager
def suspend():
    if '-s' in sys.argv:
        with tp.session.suspend():
            yield
    else:
        yield

start = time.perf_counter()

# if "-s" was specified, then suspend the Tecplot engine
# while we create the dataset, create zones, and fill
# the arrays with (random) data.
with suspend():
    fr = tp.active_frame()
    ds = fr.create_dataset('D', ['x', 'y', 'z', 'p', 'q', 'r', 'u', 'v', 'w'])
    variables = list(ds.variables())

    shape = (10, 10, 10)
    for i in range(100):
        zn = ds.add_ordered_zone('Z{}'.format(i), shape[::-1])
        for v in variables:
            zn.values(v)[:] = rand.uniform(-1000, 1000, shape).ravel()

    print(ds)

# uncomment the following line to print the time taken to create the zones
#print('Time to create zones: {:.3f} sec'.format(time.perf_counter() - start))

if '-s' not in sys.argv:
    print('Run again with "-s" to time this with the suspend context.')

if '-c' not in sys.argv:
    print('Run again with "-c" to connect to running Tecplot 360.')
    print('  To enable connections in Tecplot 360, click on:')
    print('  "Scripting..." -> "PyTecplot Connections..." -> "Accept connections"')

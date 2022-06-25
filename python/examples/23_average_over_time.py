import tecplot as tp
import os
import numpy as np

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# Load transient flow past cylinder
examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
tp.data.load_tecplot(datafile)

# Get Frame, plot and dataset handles
frame = tp.active_frame()
plot = frame.plot()
ds = frame.dataset

# Duplicate the first zone which becomes the last zone
avg_zone = ds.zone(0).copy()
avg_zone.name = "Averaged Zone"
avg_zone.strand = 0         # Using Strand = 0 sets this as a new fieldmap
avg_zone.solution_time = 0.0    # Averaged zone does not have time step

# Generate a matrix for each variable, zones by points. Then average
# (using numpy average) across all zones to get the by point value
with tp.session.suspend():
    variables = list(ds.variables())[2:]  # Skip XYZ coords
    zones = list(ds.zones())[:-1]  # Skip duplicated zone
    for var in variables:
        a = np.empty([ds.num_zones -1, avg_zone.num_points])
        for z in zones:
            values= z.values(var).as_numpy_array() # Get value at all locations
            a[z.index,:] = values         # Build matrix
        avg = np.average(a, axis=0)       # Average across all zones
        avg_zone.values(var)[:] = avg     # Add average to duplicated zone

tp.data.save_tecplot_plt('vortex_with_average.plt')

# Delete textboxes setup for LPK
for txt in frame.texts():
    frame.delete_text(txt)

# Turn on the averaged zone only.
plot.fieldmaps().show = False

plot.show_contour = True
plot.contour(0).variable = ds.variable('T(K)')
plot.fieldmap(avg_zone).show = True
plot.fieldmap(avg_zone).contour.show = True

plot.axes.y_axis.min = -0.02
plot.axes.y_axis.max = 0.02
plot.axes.x_axis.min = -0.008
plot.axes.x_axis.max = 0.04

# ensure consistent output between interactive (connected) and batch
plot.contour(0).levels.reset_to_nice()

tp.export.save_png('avg_vortex.png', width=800, supersample=3)

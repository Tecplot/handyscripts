from scipy import stats
import numpy as np
import tecplot as tp
from tecplot.constant import *

num_bins = 100
variable_of_interest = "tke"
statistic = "mean"

def create_rect_zone(imax, jmax, xminmax, yminmax):
    """
    Creates a rectangular zone and returns the zone object
    """
    cmd = """$!CreateRectangularZone
    IMAX = {}
    JMAX = {}
    X1 = {}
    X2 = {}
    Y1 = {}
    Y2 = {}""".format(imax,jmax,xminmax[0], xminmax[1], yminmax[0], yminmax[1])
    tp.macro.execute_command(cmd)
    return tp.active_frame().dataset.zone(-1)

tp.session.connect()
frame = tp.active_frame()
ds = frame.dataset
plot = frame.plot(PlotType.Cartesian2D)

# Get the variables assigned to the X and Y axes
xvar = plot.axes.x_axis.variable
yvar = plot.axes.y_axis.variable

# Define the source zone and get the variable ranges
source_zone = ds.zone("*Cell Data*")
xvals = source_zone.values(xvar)
yvals = source_zone.values(yvar)


# Create the destination grid for the statistics results
dest_zone = create_rect_zone(num_bins,num_bins, xvals.minmax(), yvals.minmax())
imax, jmax, kmax = dest_zone.dimensions
dest_zone.name = "Binned Stats {}x{}".format(imax,jmax)

# Get the "bin edges in the x and y directions
binx = dest_zone.values(xvar)[0:imax]
biny = dest_zone.values(yvar)[0:imax*jmax:imax]

# Get the variable values for which we want to compute the statistics.
values = source_zone.values(variable_of_interest)[:]

# Let scipy to the hard part
ret = stats.binned_statistic_2d(xvals[:], yvals[:], values, statistic, bins=[binx, biny])

# Get the results and do a sanity check that they're the same dimensions and our destination zone
statistics = ret.statistic
assert(len(statistics) == imax-1) # Rows are I-dimension
assert(len(statistics[0]) == jmax-1) # Columns are J-dimension

# Add a new variable to the dataset to hold the results. Make sure the new variable is cell-centered
new_variable_name = "{} - {}".format(variable_of_interest, statistic)
if new_variable_name not in ds.variable_names:
    ds.add_variable(new_variable_name, locations=[ValueLocation.CellCentered]*ds.num_zones)

# Populate and array of the results from the scipy call. Tecplot 360 cell-centered zones have
# "ghost cells" that we have to ignore. Also scipy uses NaN, which we are replacing with zero.
cell_values = dest_zone.values(new_variable_name)[:]
for j in range(jmax-1):
    for i in range(imax):
        cell_index = i+j*imax
        if i == imax-1:
            continue # Skip ghost cells
        else:
            v = statistics[i][j]
            cell_values[cell_index] = 0 if np.isnan(v) else v

# Finally, stuff the results into the destination zone
dest_zone.values(new_variable_name)[:] = cell_values

frame.load_stylesheet("final_result.sty")




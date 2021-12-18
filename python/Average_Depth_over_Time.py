""" Calculate the average of a variable for all depths per time step

Description
-----------
Create a new surface zone with averaged variables over all depths of ocean volume
data for each time step.
Note, this script only supports FVCOM data files that have a siglev variable.

Example usage:
--------------
    Windows:
       > python average_depth_over_time.py NECOFS_FVCOM_OCEAN_BOSTON_FORECAST_2048-2071.nc

         Note, this example .nc file can be found in the Getting Started Guide data download:
         https://tecplot.azureedge.net/data/360GettingStarted.zip

Necessary Modules
-----------------
numpy
    A general-purpose array-processing package. See more info here:
    https://pypi.org/project/numpy/
sys
    A module that provides variables and functions to manipulate the Python runtime environment

"""
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import numpy as np
import sys


def setup_zones(base_zone, offset, volume_zone):
    #
    # Copy and interpolate a base zone onto a new zone.
    # Parameters:
    #     base_zone - surface zone to copy
    #     offset - distance to move the copied surface
    #     volume_zone - source zone for interpolations
    # Returns the new zone with interpolated data, interp_zone.
    #
    interp_zone = base_zone.copy(share_variables=False)
    eqn = '{{siglev}} = {{siglev}}+{}'.format(offset)

    tp.data.operate.execute_equation(equation=eqn,
                                     zones=[interp_zone])
    tp.data.operate.interpolate_linear(interp_zone, volume_zone, fill_value=0)
    return interp_zone


def avg_set_of_zones(source_zones, avg_zone, timestep):
    #
    # Create a zone that will hold the averaged values.
    # Parameters:
    #    source_zones - List of zones to average over. These zones should all have the same grid.
    #    avg_zone - zone to hold the averaged values. This should have the same grid as source_zones.
    #    timestep - volume zone to derive time step info.
    #
    avg_zone.name = timestep.name + ' Depth Averaged'
    avg_zone.strand = max(z.strand for z in dataset.zones())
    avg_zone.solution_time = timestep.solution_time

    #
    # Any constant variables that shouldn't be averaged should be entered into this list.
    # Variables in the list are case sensitive.
    #
    variables_constant_through_time = ["x", "y", "lat", "lon"]

    equation = ""
    for v in tp.active_frame().dataset.variables():
        if v.name in variables_constant_through_time:
            continue
        equation = "{%s} = (" % (v.name)
        for z in source_zones:
            index = z.index + 1  # Adding 1 because execute equation uses 1-based zone indices
            equation += "{%s}[%d] +" % (v.name, index)
        equation = equation[:-1] #removing the "+" from the string
        equation += ")/ %d" % (len(source_zones))

        tp.data.operate.execute_equation(equation, zones=[avg_zone])


#
# datafile - Path to NetCFD FVCOM data file
#
if len(sys.argv)>1:
    datafile = sys.argv[1]
#
# offsets - equally spaced siglev offsets from -1 to 0
#
offsets = np.linspace(-1, 0, num=10)

#
# Uncomment the following line to connect to a running instance of Tecplot 360:
# tp.session.connect()
#
with tp.session.suspend():

    #
    # Setup dataset, plot and retrieve the list of original zones
    #
    tp.new_layout()
    dataset = tp.data.load_fvcom(datafile)
    plot = tp.active_frame().plot()
    base_vol_zones = list(dataset.zones())

    #
    # Switch to SigLev as Z variable and generate a surface from SigLev isosurface = 0
    #
    orig_z = plot.axes.z_axis.variable_index
    plot.axes.z_axis.variable = dataset.variable('siglev')
    plot.contour(0).variable = dataset.variable('siglev')
    plot.isosurface(0).isosurface_values[0] = 0
    tp.active_frame().plot(PlotType.Cartesian3D).show_isosurfaces = True
    tp.macro.execute_command('''$!ExtractIsoSurfaces
      Group = 1
      ExtractMode = SingleZone''')
    base_zone = tp.active_frame().dataset.zone(-1)
    tp.active_frame().plot(PlotType.Cartesian3D).show_isosurfaces = False

    zones_to_delete = [base_zone]

    #
    # Loop though time
    #
    for timestep in base_vol_zones:
        cur_zones = []
        print(timestep.name)

        #
        # Get volume values at given depth onto a common mesh.
        #
        for x in offsets:
            cur_zones.append(setup_zones(base_zone, x, timestep))

        #
        # Calculate the average surface of the siglev offset depth surfaces.
        #   This takes the collection of offset siglev iso-surfaces (with data
        #   that was interpolated from the volume zone at a particular time step)
        #   and averages them
        avg_set_of_zones(cur_zones, base_zone.copy(), timestep)

        #
        # Collate generated temporary zones for deletion
        #
        zones_to_delete.append(cur_zones)

    #
    # Delete zones created for interpolation before averaging
    #
    tp.active_frame().dataset.delete_zones(zones_to_delete)

    #
    # Return back to Z
    #
    plot.axes.z_axis.variable_index = orig_z

#
# Save out data
#
tp.data.save_tecplot_plt('testout.plt')

"""Compute a Time Average of a Time Strand

usage:

    > python TimeAverage.py

Necessary modules
-----------------
tpmath
    Useful mathematical utilities. This file can be found in the Tecplot GitHub:
    https://github.com/Tecplot/handyscripts/blob/master/python/tpmath.py

tputils
    Generic PyTecplot utilities. This file can be found in the Tecplot GitHub:
    https://github.com/Tecplot/handyscripts/blob/master/python/tputils.py


Description
-----------
1. To run this script we must first enable PyTecplot Connections via the
   Scripting menu in the Tecplot 360 GUI.
   The tpmath and tputils modules are also required. The script will import them
   if these modules are placed in the cwd or the same location as this .py script.
   Errors will occur if these modules aren't accessible.

2. Execute the script from a command prompt or terminal.
   This will prompt for which Strand to average. The strand number can be found
   in the Dataset Information dialog.
   A strand is simply an integer which identifies a collection of zones through time.
   Once we enter the strand number, the script will handle the zone duplication
   and execution of the formulas to average the results.

3. When the script is finished, activate the Time Average zone in 360's Zone
   Style menu to view results.

WARNING: For this script to work, all zones to be averaged MUST have the same
         number of points. For example, CONVERGE data has an adaptive mesh so each
         timestep will likely have a different number of zones. This script cannot
         handle this type of data. To compute an average, a grid with a constant
         number of points through time will be required.
"""
import tecplot as tp
import tpmath
import tputils

tp.session.connect()
in_strand = input("Which strand do you want to average? Enter the strand number or enter 'all': ")

with tp.session.suspend():
    dataset = tp.active_frame().dataset

    # Example:
    # variables_to_average = [dataset.variable("salinity"), dataset.variable("temp")]
    # constant_variables = [dataset.variable("x"), dataset.variable("y")]
    variables_to_average = dataset.variables()
    constant_variables = None

    zones_by_strand = tputils.get_zones_by_strand(dataset)
    try:
        strand_to_average = int(in_strand)
        source_zones = zones_by_strand[strand_to_average]
        tpmath.compute_average(source_zones, variables_to_average, constant_variables)
    except (TypeError, ValueError):  # Assume the user typed "all"
        for strand, source_zones in zones_by_strand.items():
            tpmath.compute_average(source_zones, variables_to_average, constant_variables)

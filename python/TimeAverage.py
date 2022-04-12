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
To run this script we must first enable PyTecplot Connections via the Scripting menu.
The tpmath and tputils modules are also required.

Execute the script from a command prompt or terminal.
This will prompt for which Strand to average.
The strand number can be found in the Dataset Information dialog.
A strand is simply an integer which identifies a collection of zones through time.
Once we enter the strand number the script will handle the zone duplication
and execution of the formulas to average the results.
When the script is finished, activate the Time Average zone to view results.

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

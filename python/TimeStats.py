"""Compute a Time Statistics of a Time Strand

usage:

    > python TimeStats.py

Necessary modules
-----------------
tpmath
    Useful Mathematical Utilities for PyTecplot
tputils
    Generic PyTecplot Utilities


Description
-----------
To run this script we must first enable PyTecplot Connections via the Scripting menu.
The tpmath and tputils modules are also required.

Execute the script from a command prompt or terminal.
This will prompt for which Strand to compute statistics.
The strand number can be found in the Dataset Information dialog.
A strand is simply an integer which identifies a collection of zones through time.
Once we enter the strand number the script will handle the zone duplication
and execution of the formulas to compute the results.
When the script is finished, activate the Time Statistics zone to view results.

"""
import tecplot as tp
import tpmath
import tputils
import time
import sys

tp.session.connect()
#in_strand = input("Which strand do you want to compute statistics? Enter the strand number or enter 'all': ")
in_strand = sys.argv[1]
chunk_size = int(sys.argv[2])
start = time.time()
with tp.session.suspend():
    dataset = tp.active_frame().dataset

    constant_variables = [dataset.variable(0), dataset.variable(1), dataset.variable(2)]
    variables_to_compute = list(dataset.variables())

    tp.macro.execute_command("$!FileConfig LoadOnDemand { UNLOADSTRATEGY = MinimizeMemoryUse }")

    zones_by_strand = tputils.get_zones_by_strand(dataset)
    try:
        strand_to_compute = int(in_strand)
        print("Computing statistics for strand: ", strand_to_compute)
        source_zones = zones_by_strand[strand_to_compute]
        tpmath.compute_statistics(source_zones, variables_to_compute, constant_variables, chunk_size=chunk_size)
    except (TypeError, ValueError):  # Assume the user typed "all"
        print("Computing statistics for all strands")
        for strand, source_zones in zones_by_strand.items():
            strand_start = time.time()
            print("Computing statistics for strand: ", strand)
            tpmath.compute_statistics(source_zones, variables_to_compute, constant_variables, chunk_size=chunk_size)
            print("Time for strand {} = {}".format(strand, time.time()-strand_start))
        
print("Elapsed time: ", time.time()-start)

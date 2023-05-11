"""Compute a Time Statistics of a Time Strand

usage:

    > python TimeStats.py <Strand Number> 
    
Input
-----
   Strand Number - Optional- Defines the set of zones to calculate the average over. 
        If not supplied, all strands will be calculated. 
        Strand number can be found in Dataset Information dialog. 
   

Description
-----------
This script assumes that a transient dataset is loaded into 360 with PyTecplot
Connections enabled via the Scripting menu. The result of the script will be two
new zones where one is the minimum value for each node through time and the other zone 
will have the maximum value for each node through time. 


Necessary modules
-----------------
tpmath
    Useful Mathematical Utilities for PyTecplot
tputils
    Generic PyTecplot Utilities


"""
import tecplot as tp
import tpmath
import tputils
import time
import sys

tp.session.connect()

try:
    in_strand = int(sys.argv[1])
except: 
    in_strand = None


start = time.time()
with tp.session.suspend():
    dataset = tp.active_frame().dataset
    plot = tp.active_frame().plot()
    
    # Assumes that the grid variables are constant and wont be calculated.
    constant_variables = tputils.get_axes_variable_assignment(plot)
    variables_to_compute = list(dataset.variables())

    tp.macro.execute_command("$!FileConfig LoadOnDemand { UNLOADSTRATEGY = MinimizeMemoryUse }")

    zones_by_strand = tputils.get_zones_by_strand(dataset)
    if in_strand != None:         
        print("Computing statistics for strand: ", in_strand)
        source_zones = zones_by_strand[in_strand]
        tpmath.compute_statistics(source_zones, variables_to_compute, constant_variables)
    else: 
        print("Computing statistics for all strands")
        for strand, source_zones in zones_by_strand.items():
            strand_start = time.time()
            print("Computing statistics for strand: ", strand)
            tpmath.compute_statistics(source_zones, variables_to_compute, constant_variables)
            print("Time for strand {} = {}".format(strand, time.time()-strand_start))
        
print("Elapsed time: ", time.time()-start)

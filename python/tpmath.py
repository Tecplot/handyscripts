"""Useful Mathematical Utilities for PyTecplot
This file contains functions we have found to be useful across multiple
scripts that are mathematical or computational in nature. It is meant to
be imported into a running python script with ``import tpmath``.
"""
import tecplot as tp
import tputils


#
# Computes the sum of the specified variable for the source_zones and
# applies the result to the destination zone.  Typical usage would be
# to sum all the values in a specific strand over time.
#
# All source zones must have the same number of nodes
#
def compute_sum(variable, source_zones, dest_zone, chunk_size=50):
    # Tecplot equation syntax has a length limit, so we chunk the summation to ensure
    # that we don't overflow that length limit.  In testing the limit is ~300 zones, but
    # it depends on the length of the variable name as well.
    #
    # Larger chunk_size will typically result in faster run times, but will consume
    # more RAM since more zones need to be loaded simultaneously.
    with tputils.ForceEditableVariable(variable):
        tp.data.operate.execute_equation("{%s} = 0" % (variable.name), zones=[dest_zone])
        for zones in tputils.chunks(source_zones, chunk_size):
            equation = "{%s} = {%s}" % (variable.name, variable.name)
            for z in zones:
                zone_num = z.index + 1  # Adding 1 because execute equation uses 1-based zone indices
                equation += " + {%s}[%d]" % (variable.name, zone_num)
            tp.data.operate.execute_equation(equation, zones=[dest_zone])

#
# Computes the min or max of the specified variable for the source_zones and
# applies the result to the destination zone. Typical usage would be
# to find the minimum value over all the values in a specific strand over time.
#
# All source zones must have the same number of nodes
#
def compute_minmax(variable, source_zones, dest_zone, operator='<'):
    with tputils.ForceEditableVariable(variable):
        # Initialize with values from the first source zone
        print(variable.name)
        equation = "{{{var}}} = {{{var}}}[{zone}]".format(var=variable.name, zone=source_zones[0].index+1)
        tp.data.operate.execute_equation(equation, zones=[dest_zone])

        for zone in source_zones:
            equation = "{{{v}}} = IF({{{v}}} {operator} {{{v}}}[{z}], {{{v}}}, {{{v}}}[{z}])".format(v=variable.name, operator=operator, z=zone.index+1)
            print(equation)
            tp.data.operate.execute_equation(equation, zones=[dest_zone])


#
# Computes the average of the supplied zones for each variable supplied. Each
# zone must have the same number of points.
#
# Creates a new zone called "Time Average - nnn" where nnn is the strand number
# of the first source_zones element.  The resulting zone will have variable values of
# zero for any variable not supplied to this function
#
# source_zones - the set of zones to use for computing the average
# variables_to_average - the variables for which to average
# constant_variables - any variables that are constant across the set
#   of source_zones. Often these are X,Y,Z variables.
# chunk_size - The number of zones to simultaneously load in order to compute the
#   sum. Larger numbers will typically result in faster run times, but will consume
#   more RAM.
#
def compute_average(source_zones, variables_to_average, constant_variables=None, chunk_size=50):
    dataset = source_zones[0].dataset
    avg_zone = dataset.copy_zones(source_zones[0])[0]
    strand = avg_zone.strand
    avg_zone.name = "Time Average - " + str(strand)
    avg_zone.strand = 0
    avg_zone.solution_time = 0
    avg_zone.aux_data['source_strand'] = str(strand)
    avg_zone.aux_data['zone_type'] = "Average"

    for v in dataset.variables():
        # Skip over the constants
        if constant_variables and v in constant_variables:
            continue

        with tputils.ForceEditableVariable(v):
            if v in variables_to_average:
                print("Computing average for strand: {}, var: {}".format(strand, v.name))
                compute_sum(v, source_zones, avg_zone, chunk_size=chunk_size)
                equation = "{%s} = {%s}/%d"%(v.name, v.name, len(source_zones))
                tp.data.operate.execute_equation(equation, zones=[avg_zone])
            else:
                # If the variable is not to be averaged, set it to zero so we don't
                # mislead the user with results that were copied from a source zone.
                # Making the variable passive would be better, but there's currently
                # no way to convert a variable to passive.
                tp.data.operate.execute_equation("{%s} = 0"%(v.name), zones=[avg_zone])
    return avg_zone

#
# Computes the phase average of the supplied zones for each variable supplied. 
# Over number of zones_per_timeperiod specified. Each zone must have the same number of points.
#
# Creates a new zones called "phase n.nn pi - oldName" where n.nn is the phase defined by 
# number of zones in one timeperiod. The resulting zones will have variable values of
# zero for any variable not supplied to this function
#
# source_zones - the set of zones to use for computing the phase average
# zones_per_timeperiod - number of zones in one timeperiod
# variables_to_average - the variables for which to average
# constant_variables - any variables that are constant across the set
#   of source_zones. Often these are X,Y,Z variables.
# chunk_size - The number of zones to simultaneously load in order to compute the
#   sum. Larger numbers will typically result in faster run times, but will consume
#   more RAM.
#
def compute_phaseAverage(source_zones, zones_per_timeperiod, variables_to_average, constant_variables=None, chunk_size=50):
    # currently implemented for constant delta t solution files
    dataset = source_zones[0].dataset
    phAvg_zones = dataset.copy_zones(source_zones[slice(zones_per_timeperiod)])
    # rename zones
    for zone, i in zip(phAvg_zones, range(zones_per_timeperiod)):
        zone.name = "%s %.2f pi - %s" % ('phase', 2*i/zones_per_timeperiod, zone.name)
        zone.strand = dataset.num_zones
    # all_zNames = dataset.zone_names
    # phAvg_zNames = ["%s %.2f pi - %s" % ('phase', 2*i/zones_per_timeperiod, all_zNames[i]) for i in range(zones_per_timeperiod)]
    # dataset.zone_names[-zones_per_timeperiod:] = phAvg_zNames[:]
    for i in range(zones_per_timeperiod):
        #list zones with same phase
        phase_i_zones = source_zones[slice(i, len(source_zones), zones_per_timeperiod)]
        
        for v in dataset.variables():
            # Skip over the constants
            if constant_variables and v in constant_variables:
                continue
            
            with tputils.ForceEditableVariable(v):
                if v in variables_to_average:
                    print("Computing average for phase: {} pi, var: {}".format(i*2/zones_per_timeperiod, v.name))
                    compute_sum(v, phase_i_zones, phAvg_zones[i], chunk_size=chunk_size)
                    equation = "{%s} = {%s}/%d"%(v.name, v.name, len(phase_i_zones))
                    tp.data.operate.execute_equation(equation, zones=[phAvg_zones[i]])
                else:
                    # If the variable is not to be averaged, set it to zero so we don't
                    # mislead the user with results that were copied from a source zone.
                    # Making the variable passive would be better, but there's currently
                    # no way to convert a variable to passive.
                    tp.data.operate.execute_equation("{%s} = 0"%(v.name), zones=[phAvg_zones[i]])
    return phAvg_zones

#
# Computes the min/max of the supplied zones for each variable supplied. Each
# zone must have the same number of points.
#
# Creates a new zones called "Time Min - nnn" and "Time Max - nnn" where nnn is 
# the strand number of the first source_zones element.  The resulting zone will 
# have variable values of zero for any variable not supplied to this function.
#
# source_zones - the set of zones to use for computing the statistics 
# variables_to_compute - the variables for which to compute statistics 
# constant_variables - any variables that are constant across the set
#   of source_zones. Often these are X,Y,Z variables.
#
def compute_statistics(source_zones, variables_to_compute, constant_variables=None):
    dataset = source_zones[0].dataset
    min_zone = dataset.copy_zones(source_zones[0])[0]
    max_zone = dataset.copy_zones(source_zones[0])[0]
    strand = source_zones[0].strand

    min_zone.name = "Time Min - " + str(strand)
    min_zone.strand = 0
    min_zone.solution_time = 0
    min_zone.aux_data['source_strand'] = str(strand)
    min_zone.aux_data['zone_type'] = "Min"

    max_zone.name = "Time Max - " + str(strand)
    max_zone.strand = 0
    max_zone.solution_time = 0
    max_zone.aux_data['source_strand'] = str(strand)
    max_zone.aux_data['zone_type'] = "Max"

    for v in dataset.variables():
        # Skip over the constants
        if constant_variables and v in constant_variables:
            continue

        if v in variables_to_compute:
            print("Computing min/max for strand: {}, var: {}".format(strand, v.name))
            compute_minmax(v, source_zones, min_zone, operator="<")
            compute_minmax(v, source_zones, max_zone, operator=">")
        else:
            # If the variable is not to be averaged, set it to zero so we don't
            # mislead the user with results that were copied from a source zone.
            # Making the variable passive would be better, but there's currently
            # no way to convert a variable to passive.
            tp.data.operate.execute_equation("{%s} = 0"%(v.name), zones=[min_zone, max_zone])
    return (min_zone, max_zone)

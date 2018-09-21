import tecplot as tp
from tecplot.constant import *
from tecplot.tecutil import _tecutil
from tecplot.exception import *

#
# Surveys all zones associated with the supplied fieldmap
# and returns the variable min/max as a tuple 
#
def fieldmap_minmax(fieldmap, variable):
    min_val = None
    max_val = None
    for z in fieldmap.zones:
        if min_val == None:
            min_val, max_val = z.values(variable).minmax()
        else:
            cur_minmax = z.values(variable).minmax()
            min_val = min(min_val, cur_minmax[0])
            max_val = max(max_val, cur_minmax[1])
    return (min_val, max_val)
    
#
# Attaches the specified dataset to the frame. The frame
# must not have a dataset yet.
# 
# Example:
#   dataset = tp.active_frame().dataset
#   new_frame = tputils.active_page().add_frame()
#   tputils.attach_dataset(new_frame, dataset)
#
def attach_dataset(frame, dataset):
    if not _tecutil.FrameSetDataSet(dataset.uid,frame.uid): 
        raise TecplotSystemError()
    
#
# Returns the largest strand number in the supplied dataset
#
def max_strand(dataset):
    result = 0
    for z in dataset.zones():
        result = max(result, z.strand)
    return result
    
# Returns a dictionary of strand to zone list
# Example - get all the zones associated with strand #3:
#   zones_by_strand = get_zones_by_strand(tp.active_frame().dataset)
#   zones = zones_by_strand[3]
def get_zones_by_strand(dataset):
    zones_by_strand = {}
    for z in dataset.zones():
        if z.strand == 0:
            continue    
        if z.strand in zones_by_strand: 
            zones_by_strand[z.strand].append(z)
        else: 
            zones_by_strand[z.strand] = [z]
    return zones_by_strand

def get_zones_by_strand_in_active_frame():
    import ctypes
    from tecplot.tecutil import IndexSet
    zones_by_strand = {}

    ptr = _tecutil.DataSetGetStrandIDs()
    strands = ctypes.cast(ptr, IndexSet)
    strands = [s+1 for s in strands]

    dataset = tp.active_frame().dataset
    for s in strands:
        ptr = _tecutil.DataSetGetZonesForStrandID(s)
        zone_indices = ctypes.cast(ptr, IndexSet)
        zones = [dataset.zone(z) for z in zone_indices]
        zones_by_strand[s] = zones
    return zones_by_strand

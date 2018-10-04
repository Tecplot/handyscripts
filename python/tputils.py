"""Generic PyTecplot Utilities

These are some generic functions that we have found useful across several
applications when using PyTecplot in either batch or connected mode. This
file is meant to be imported as a Python module as in this example where we
attach the dataset of the active frame a newly created frame:

    >>> import tecplot as tp
    >>> import tputils
    >>> frame = tp.active_frame()
    >>> new_frame = tp.active_page().add_frame()
    >>> tputils.attach_dataset(new_frame, frame.dataset)

"""
import ctypes

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot.tecutil import _tecutil


def fieldmap_minmax(fieldmap, variable):
    """Data limits for a given varible across all zones in a fieldmap"""
    limits = None
    for z in fieldmap.zones:
        if limits is None:
            limits = z.values(variable).minmax()
        else:
            low, high = z.values(variable).minmax()
            limits = min(limits[0], low), max(limits[1], high)
    return limits


def attach_dataset(frame, dataset):
    """Attach a dataset to a specific frame

    The frame must not have a dataset yet.

    Example:

        >>> import tecplot as tp
        >>> import tputils
        >>> dataset = tp.active_frame().dataset
        >>> new_frame = tp.active_page().add_frame()
        >>> tputils.attach_dataset(new_frame, dataset)
    """
    if not _tecutil.FrameSetDataSet(dataset.uid, frame.uid):
        raise TecplotSystemError()


def max_strand(dataset):
    """Returns the largest strand number in the supplied dataset"""
    return max(z.strand for z in dataset.zones())


def get_zones_by_strand(dataset):
    """Returns a dictionary of strand to zone list

    This example shows getting all the zones associated with ``strand == 3``:

        >>> import tecplot as tp
        >>> zones_by_strand = get_zones_by_strand(tp.active_frame().dataset)
        >>> zones = zones_by_strand[3]
    """
    zones_by_strand = {}
    for z in dataset.zones():
        strand = z.strand
        if strand > 0:
            if strand not in zones_by_strand:
                zones_by_strand[strand] = []
            zones_by_strand.append(z)
    return zones_by_strand


def get_zones_by_strand_in_active_frame():
    """Returns a dictionary of strands to zone list for the active frame"""
    ptr = _tecutil.DataSetGetStrandIDs()
    strands = ctypes.cast(ptr, tp.tecutil.IndexSet)
    strands = [s + 1 for s in strands]
    strands.dealloc()

    zones_by_strand = {}
    dataset = tp.active_frame().dataset
    for s in strands:
        ptr = _tecutil.DataSetGetZonesForStrandID(s)
        zone_indices = ctypes.cast(ptr, tp.tecutil.IndexSet)
        zones = [dataset.zone(z) for z in zone_indices]
        zone_indices.dealloc()

        zones_by_strand[s] = zones

    return zones_by_strand

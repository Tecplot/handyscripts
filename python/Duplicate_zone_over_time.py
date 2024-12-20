import tecplot as tp
import numpy as np

DUPE_ZONE = 3

tp.session.connect()
ds = tp.active_frame().dataset
strand_of_interest = ds.zone(DUPE_ZONE).strand

# set a reference to 'all zones' as they appear before manipulation
all_zones = list(ds.zones())
zones_to_dupe = []
for zone in all_zones:
    if zone.strand == strand_of_interest:
        zones_to_dupe.append(zone.index)

ds.copy_zones(zones_to_dupe)


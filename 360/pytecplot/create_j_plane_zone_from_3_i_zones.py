"""Create zone 3 from zones 0, 1, and 2 using x, y, and z values.

This script expects:
    zone 0: ordered line zone with dimensions (I, 1, 1)
    zone 1: ordered line zone with dimensions (I, 1, 1)
    zone 2: ordered line zone with dimensions (I, 1, 1)

It creates a new ordered zone with dimensions (I, 3, 1). The x, y, and z
values from zones 0, 1, and 2 are copied into the J-planes of the new zone.
If the dataset initially contains only zones 0, 1, and 2, then the new zone
will be zone 3.

Run with:
    python create_j_plane_zone_from_3_i_zones.py -c
"""

import sys

import numpy as np
import tecplot as tp


def validate_line_zone(zone, expected_i):
    dimensions = tuple(zone.dimensions)
    if dimensions[1:] != (1, 1):
        raise ValueError(
            f"Zone {zone.index} ('{zone.name}') must have dimensions (I, 1, 1); got {dimensions}."
        )
    if dimensions[0] != expected_i:
        raise ValueError(
            f"Zone {zone.index} ('{zone.name}') must have I dimension {expected_i}; got {dimensions[0]}."
        )


if '-c' in sys.argv:
    tp.session.connect()

dataset = tp.active_frame().dataset
if dataset is None:
    raise RuntimeError("No active dataset is available in the current Tecplot frame.")

if dataset.num_zones < 3:
    raise RuntimeError(f"Expected at least 3 zones in the dataset; found {dataset.num_zones}.")

zone0 = dataset.zone(0)
zone1 = dataset.zone(1)
zone2 = dataset.zone(2)

i_max = zone0.dimensions[0]
validate_line_zone(zone0, i_max)
validate_line_zone(zone1, i_max)
validate_line_zone(zone2, i_max)

for variable_name in ('x', 'y', 'z'):
    dataset.variable(variable_name)



with tp.session.suspend():
    new_zone = dataset.add_ordered_zone('CombinedJPlanes', (i_max, 3, 1))

    x0 = np.asarray(zone0.values('x').as_numpy_array()).reshape(i_max)
    x1 = np.asarray(zone1.values('x').as_numpy_array()).reshape(i_max)
    x2 = np.asarray(zone2.values('x').as_numpy_array()).reshape(i_max)
    new_zone.values('x')[:] = np.concatenate((x0, x1, x2))

    y0 = np.asarray(zone0.values('y').as_numpy_array()).reshape(i_max)
    y1 = np.asarray(zone1.values('y').as_numpy_array()).reshape(i_max)
    y2 = np.asarray(zone2.values('y').as_numpy_array()).reshape(i_max)
    new_zone.values('y')[:] = np.concatenate((y0, y1, y2))

    z0 = np.asarray(zone0.values('z').as_numpy_array()).reshape(i_max)
    z1 = np.asarray(zone1.values('z').as_numpy_array()).reshape(i_max)
    z2 = np.asarray(zone2.values('z').as_numpy_array()).reshape(i_max)
    new_zone.values('z')[:] = np.concatenate((z0, z1, z2))

print(
    f"Created zone {new_zone.index} ('{new_zone.name}') with dimensions {tuple(new_zone.dimensions)} "
    f"from zones {zone0.index}, {zone1.index}, and {zone2.index}."
)

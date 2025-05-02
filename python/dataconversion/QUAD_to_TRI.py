"""Converts an FE Quad zone to an FE Triangle zone

usage:

    > python QUAD_to_TRI.py

Description
-----------

This connected-mode script creates a new FE Triangle zone
from a chosen pre-existing FE Quad zone that only has 3 unique
nodes per cell.
"""


import tecplot as tp
from tecplot.constant import ZoneType


def quad_to_tri(zn, ds, zone_name):
    nmap = zn.nodemap[:]
    n_cells = zn.num_elements
    n_nodes = zn.num_points

    # Check if nodemap is truly an FE Triangle nodemap
    is_tri = any(len(set(lst)) == 3 for lst in nmap)

    if not is_tri:
        print("Not an FE Triangle zone")
        return

    # Create FE Triangle nodemap from FE Quad nodemap
    tri_nmap = [set(m) for m in nmap]

    new_zn = ds.add_fe_zone(ZoneType.FETriangle, zone_name, n_nodes, n_cells)

    # Assign new zone with nodemap and variable values
    new_zn.nodemap[:] = tri_nmap
    for i in range(ds.num_variables):
        new_zn.values(i)[:] = zn.values(i)[:]


if __name__ == "__main__":
    tp.session.connect()

    ds = tp.active_frame().dataset

    zones = ds.zone_names

    # Print all zones to choose from
    print("Zone list:")
    for i, z in enumerate(zones):
        print(f"{i+1}. {z}")

    choice = int(input("Which zone would you like to convert? "))
    zone_name = input("New zone name: ")

    # Take zone input and run the conversion
    zone = ds.zone(choice-1)

    # Attempt to convert zone to FE Triangle zone
    quad_to_tri(zone, ds, zone_name)

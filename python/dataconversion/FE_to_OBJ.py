"""Convert and export FE surfaces into Wavefront (*.obj) format

This provides another geometry export format besides converting FE data to STL
files. See FE_to_STL.py for example:
https://github.com/Tecplot/handyscripts/blob/master/python/dataconversion/FE_to_STL.py

Usage:
    > python FE_to_OBJ.py output_file.obj

Necessary modules
-----------------
tecplot
    Tecplot Python API (PyTecplot). More installation information here:
    https://www.tecplot.com/docs/pytecplot/install.html

Description
-----------
The most common use of this script is to convert streamtrace rods and ribbons
into a geometry format which can be shared with the designers of a CFD simulation.

One of the key bits of information is that the Python script only works with FE
data - but Tecplot 360 extracts stream rods/ribbons as IJ-Ordered.  Using the
Extract>Blanked Zone dialog is a trick to convert Ordered data to FE.

Procedure:
1. Before running this script, we must first enable PyTecplot Connections in the
   Tecplot 360 GUI via Scripting>PyTecplot Connections... and activate Accept Connections
2. In the GUI, place the volume streamtrace rods/ribbons
3. Extract these streamtrace rods/ribbons (Data>Extract>Streamtraces...)
4. Convert these zones to FE data using Data>Extract>Blanked Zones...
   Select the extracted streamtrace zones and continue through the blanking message.
5. From the command line, run this script
"""

import tecplot as tp
from tecplot.constant import *

"""
Wavefront OBJ format is simple vertices and face connectivity
Vertex normals are also supported, but I'm not writing them yet and
not sure if they're even required.
v -0.5 -0.5 0.0
v +0.5 -0.5 0.0
v +0.5 +0.5 0.0
v -0.5 +0.5 0.0
f 1 2 3 4
"""

def write_vertices(zone, outfile):
    assert(type(zone) is not tp.data.zone.OrderedZone)
    # Assuming the first three variables are the spatial variables: X,Y,Z
    xvals = zone.values(0)[:]
    yvals = zone.values(1)[:]
    zvals = zone.values(2)[:]
    for x,y,z in zip(xvals, yvals, zvals):
        outfile.write("v {} {} {}\n".format(x,y,z))

def write_poly_facets_fast(zone, outfile, offset):
    assert(type(zone) == tp.data.zone.PolyFEZone)
    from tecplot.data.facemap import Elementmap
    max_facet = 0
    fm = zone.facemap

    # Grab the internal element map for faster access
    emap = Elementmap(zone)

    for e in range(zone.num_elements):
        unique_element_nodes = []
        for f in emap.faces(e):
            left_elem = fm.left_element(f)
            right_elem = fm.right_element(f)
            assert(fm.num_nodes(f) == 2) # Global face, so no element
            if left_elem == e:
                unique_element_nodes.append(offset+1+fm.node(f,0))
            else:
                unique_element_nodes.append(offset+1+fm.node(f,1))
        max_facet = max(max_facet, max(unique_element_nodes))
        outfile.write("f")
        if "Z Grid K Unit Normal" in zone.dataset.variable_names:
            # Write vertex and vertex normal index, which are the same node number
            for f in unique_element_nodes:
                outfile.write(" {}//{}".format(f,f))
        else:
            for f in unique_element_nodes:
                outfile.write(" {}".format(f,f))
        outfile.write("\n")
    return max_facet


def write_fe_facets(zone, outfile, offset):
    assert(type(zone) is tp.data.zone.ClassicFEZone)
    max_facet = 0
    faces = zone.nodemap[:]
    # Surfaces are facets 'f'. Lines are 'l'
    attribute = 'f' if zone.rank == 2 else 'l'
    for f in faces:
        one_based_facets = [x+1+offset for x in f]
        max_facet = max(max_facet, max(one_based_facets))
        str_facets = ' '.join(map(str,one_based_facets))
        outfile.write("{} {}\n".format(attribute, str_facets))
    return max_facet

def write_facets(zone, outfile, offset):
    assert(type(zone) is not tp.data.zone.OrderedZone)
    if type(zone) is tp.data.zone.ClassicFEZone:
        return write_fe_facets(zone, outfile, offset)
    elif type(zone) is tp.data.zone.PolyFEZone:
        return write_poly_facets_fast(zone, outfile, offset)
    return 0

def write_zones_to_wavefront_obj(zones, file_name):
    with open(file_name, 'w') as f:
        offset = 0
        for z in zones:
            if z.rank == 3:
                print("Skipping volume zone: ", z.name)
                continue
            elif type(z) == tp.data.zone.OrderedZone:
                print("Skipping Ordered zone: ", z.name)
                continue
            print("Writing: ", z.name)
            ## Write ObjectName and/or GroupName
            #f.write("o {}\n".format(z.name))
            # Group results in separate items in Maya and is preferred
            f.write("g {}\n".format(z.name))
            write_vertices(z, f)
            offset = write_facets(z, f, offset)

def test():
    import sys
    outfile = sys.argv[1]
    zone_pattern = input("Enter zone name to write (can use wild cards, e.g. 'Extracted Streamtrace*')...")
    tp.session.connect()
    ds = tp.active_frame().dataset
    zones = ds.zones(zone_pattern)
    write_zones_to_wavefront_obj(zones, outfile)

if __name__ == '__main__':
    test()

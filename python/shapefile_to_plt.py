"""Convert Shapefiles to Tecplot plt format

usage:

    > python shapefile_to_plt.py shapefile.shp outfile.plt

Necessary modules
-----------------
pyshp
    The Python Shapefile Library (pyshp) reads and writes ESRI Shapefiles in pure Python.
    https://pypi.python.org/pypi/pyshp
    https://www.esri.com/library/whitepapers/pdfs/shapefile.pdf


Description
-----------
This script is used to convert Shapefiles (.shp) to Tecplot plt format.
Users will need to answer a few questions about their shapefile to accurately
import into Tecplot format.

First select a conversion type: Convert to a single zone or one zone per shape.
Next select variable names to use: x/y or lon/lat
Finally, if using one zone per shape, select the column to name the zones

After running the script, append the new plt file to the active frame and match the
variable names.

"""
import sys
import os
import time
import shapefile as sf
import tecplot as tp
from tecplot.constant import *


def create_connectivity_list(shape, element_offset=0):
    """Use the element indices for each shape to create the connectivity list"""
    num_points = len(shape.points)
    num_parts = len(shape.parts)
    elements = []

    for i in range(num_parts):
        # parts[] returns the point index at the start of each part
        # These values will define the connectivity list of the line segments
        p1 = shape.parts[i]

        # Check to see if we're at the last part so we don't over index the list
        if i < num_parts - 1:
            p2 = shape.parts[i + 1] - 1
        else:
            p2 = num_points - 1

        p1 += element_offset
        p2 += element_offset

        # Create the connectivity list for this part. Each point is connected to the next
        for i in range(p1, p2):
            elements.append((i, i + 1))
    return elements


def convert_to_single_zone(s, zone_name, dataset):
    """Loop over all the shapes, collecting their point values and generating
    the FE-Line Segment connectivity list."""
    x = []
    y = []
    elements = []
    num_points = 0

    for shapeRec in s.shapeRecords():
        elements.extend(create_connectivity_list(shapeRec.shape, num_points))
        x.extend([n[0] for n in shapeRec.shape.points])
        y.extend([n[1] for n in shapeRec.shape.points])
        num_points += len(shapeRec.shape.points)

    # Now that we have the points and connectivity list we add a zone to the dataset
    zone = dataset.add_fe_zone(ZoneType.FELineSeg, zone_name, num_points, len(elements))
    zone.values(0)[:] = x
    zone.values(1)[:] = y
    zone.nodemap[:] = elements


def convert_to_one_zone_per_shape(s, name_index, dataset):
    """Create a Tecplot zone for each shape"""
    for i, shapeRec in enumerate(s.shapeRecords()):
        # Extract the zone name from the appropriate location in the shape record
        zone_name = shapeRec.record[name_index]
        if len(zone_name) == 0:
            zone_name = 'NONE'
        num_points = len(shapeRec.shape.points)

        elements = create_connectivity_list(shapeRec.shape)
        x = [n[0] for n in shapeRec.shape.points]
        y = [n[1] for n in shapeRec.shape.points]

        # Create the Tecplot zone and add the point data as well as the connectivity list
        zone = dataset.add_fe_zone(ZoneType.FELineSeg, zone_name, num_points, len(elements))
        zone.values(0)[:] = x
        zone.values(1)[:] = y
        zone.nodemap[:] = elements

        # Print dots to give the user an indication that something is happening
        sys.stdout.write('.')
        sys.stdout.flush()


def get_var_names():
    """Choose the variable names to use"""
    print("1 - Use 'x' and 'y'")
    print("2 - Use 'lon' and 'lat'")
    var_name_choice = int(input("Enter your choice for variable names: ")) - 1
    return var_name_choice


def get_name_index(shape_reader):
    """Displays Shapefile column used to name zones"""
    first_record = shape_reader.shapeRecords()[0].record
    # Record is the "column" information for the shape
    index = 1
    for f, r in zip(shape_reader.fields[1:], first_record):
        print(index, "- ", f[0], ": ", r)
        index += 1
    name_index = int(input("Enter the index to use for zone names: ")) - 1
    return name_index


def get_conversion_option(shape_records):
    """Prompts user for conversion options"""
    print("1 - Convert to a single zone")
    print("2 - Convert to one zone per shape (%d zones) (this can take a while)" % (len(shape_records)))
    import_option = int(input("Enter your conversion selection: "))
    return import_option


def main(shapefilename, outfilename):
    # define index from record for zone name
    s = sf.Reader(shapefilename)
    shape_records = s.shapeRecords()

    conversion_option = get_conversion_option(shape_records)

    if get_var_names() == 0:
        x_var_name = 'x'
        y_var_name = 'y'
    else:
        x_var_name = 'lon'
        y_var_name = 'lat'
    dataset = tp.active_frame().create_dataset("Shapefile", [x_var_name, y_var_name])

    if conversion_option == 1:  # Single Zone
        start = time.time()
        convert_to_single_zone(s, os.path.basename(shapefilename), dataset)
    else:  # One Zone per Shape
        name_index = get_name_index(s)
        start = time.time()
        convert_to_one_zone_per_shape(s, name_index, dataset)
    tp.data.save_tecplot_plt(outfilename)
    print("Elapsed time: ", time.time() - start)


if len(sys.argv) != 3:
    print("Usage:\nshapefile_to_plt.py shapefile.shp outfile.plt")
else:
    shapefilename = sys.argv[1]
    outfilename = sys.argv[2]
    main(shapefilename, outfilename)

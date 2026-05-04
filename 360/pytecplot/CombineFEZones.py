"""Merge multiple FE zones into a single zone 

usage:

    > python CombineFEZones.py


Description
-----------
This script will load a sample file and merge all FE zones into a single zone. 
It supports a mixture of Nodal and CellCentered variables. 

"""


import os
import tecplot as tp
from tecplot.constant import *


tp.session.connect()


# Remove the following lines if you already have a dataset
#tp.new_layout()
#examples_directory = tp.session.tecplot_examples_directory()
# tp.data.load_tecplot(os.path.join(examples_directory, "SimpleData", "F18.plt"))
# Add CellCentered variable

tp.data.operate.execute_equation(equation='{S_CC} = {S}',
    value_location=ValueLocation.CellCentered)

ds = tp.active_frame().dataset
#
# Modify the set of zones to combine here.  All zones must be "Classic FE" and be of the same type
#
zones = list(ds.zones())


#
# Survey all the input zones to determine the type, total points, and total elements
#
num_points = 0
num_elements = 0

zone_type = None
for z in zones:
    if not zone_type:
        zone_type = z.zone_type
    else:
        # All zones must be the same type
        assert(z.zone_type == zone_type)
    num_points += z.num_points
    num_elements += z.num_elements

#
# Get variable locations from the first zone
#
var_locations = [v.values(0).location for v in ds.variables()]
#
# Create the new zone using the total point/element count
#
new_zone = ds.add_fe_zone(zone_type, "Combined Zone", num_points, num_elements,
                          locations=var_locations)

#
# Populate the new zone, being sure to offset the point and element indices
#
start_point = 0
start_point_cc = 0
end_point_cc = 0
start_element = 0
for z in zones:
    print("Processing Zone: ", z.name)
    for v in ds.variables():
        print("  Processing Variable: ", v.name)
        vals = new_zone.values(v)
        if vals.location == tp.constant.ValueLocation.Nodal:
            end_point = start_point + z.num_points
            vals[start_point:end_point] = z.values(v).as_numpy_array()
        else: 
            end_point_cc = start_point_cc + z.num_elements
            vals[start_point_cc:end_point_cc] = z.values(v).as_numpy_array()

    node_offset = start_point
    start_point = end_point
    start_point_cc = end_point_cc


    print("  Setting Nodemap")
    offset_nodemap = []
    for element in z.nodemap[:]:
        offset_element = []
        for node in element:
            offset_element.append(node+node_offset)
        offset_nodemap.append(offset_element)
    end_element = start_element + z.num_elements
    new_zone.nodemap[start_element:end_element] = offset_nodemap

    start_element = end_element

print("Done")
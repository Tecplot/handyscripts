'''
This script exports all zones to a CSV file that have zone names matching a
defined regular expression. This script assumes all nodal data.

Usage:
    1. Redefine `OUTPUT_FILE` and `REGEX` below to define the output
    CSV location and regular expresison to match with.
    2. Start Tecplot 360 and load data
    3. Turn on PyTecplot connections:
        via Scripting > PyTecplot Connections... > Accept Connections
    4. Run script: `python export_data_regex.py`

NOTE: The CSV format is as follows:

Zone Name, Solution time, Variable1, Variable2, Variable3, ... , VariableN
first matched zone name, solution time of zone, first value of variable 1 for zone, ... , first value of variable n for zone
first matched zone name, solution time of zone, second value of variable 1 for zone, ... , second value of variable n for zone
first matched zone name, solution time of zone, third value of variable 1 for zone, ... , third value of variable n for zone
.
.
.
nth matched zone name, solution time of zone, first value of variable 1 for zone, ... , first value of variable n for zone
nth matched zone name, solution time of zone, second value of variable 1 for zone, ... , second value of variable n for zone
nth matched zone name, solution time of zone, third value of variable 1 for zone, ... , third value of variable n for zone
.
.
.
'''
import tecplot as tp
import re
import pandas as pd
import numpy as np
from numpy.dtypes import StringDType

OUTPUT_FILE = "out.csv"
REGEX = r"zonename_1"

# Connect to running instance of Tecplot 360
# - Make sure to turn on PyTecplot connections
#   via Scripting > PyTecplot Connections... > Accept Connections
tp.session.connect()

f = tp.active_frame()
dataset = f.dataset
zone_names = dataset.zone_names

# Find which zone names match the REGEX and add them to list
matched_zones = list(dataset.zones(re.compile(REGEX)))

# Put all zones & data into csv
columns = ["Zone Name", "Solution Time"]
columns.extend(dataset.variable_names)

total_num_pts = 0
for zn in matched_zones:
    total_num_pts += zn.num_points

num_vars = dataset.num_variables
data_arrays = np.empty((total_num_pts, len(columns)), dtype=StringDType())
cur_row = 0
for zn in matched_zones:
    zn_num_points = zn.num_points
    data_arrays[cur_row:cur_row+zn_num_points, 0] = [zn.name] * zn_num_points
    data_arrays[cur_row:cur_row+zn_num_points, 1] = [zn.solution_time] * zn_num_points
    for var in range(num_vars):
        data_arrays[cur_row:cur_row+zn_num_points, var+2] = zn.values(var)[:]
    cur_row += zn_num_points

output = pd.DataFrame(data=data_arrays, columns=columns)

output.to_csv(OUTPUT_FILE, index=False)

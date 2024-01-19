"""  
    Takes value in range of x and outputs interpolated y-value. 
    A way to probe for func values of XY plots.

    Example below uses customlabels.plt datadset included with pytecplot and probes a value of the "Concentration" variable in XY plot. 
"""
import sys
import tecplot as tp
from os import path
from tecplot.constant import *
from scipy.interpolate import interp1d

if '-c' in sys.argv:
	tp.session.connect()

#load data
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'CustomLabels.plt') 
dataset = tp.data.load_tecplot(datafile)

# Select Variable by name or by zone number
# remember tecplot is 1 indexed so 0 refers to the 1st tecplot zone
zname = "Concentration"
ds = tp.active_frame().dataset
zn = ds.zone(zname)


# use interpolation of X and Y axes to get value.
def probe_func_at(value):
    
    # Uses default X and Y axes
    x_array = zn.values(0)[:]
    y_array = zn.values(1)[:]

    if value > max(x_array) or value < min(x_array):
        print("value not in domain of given x_array")
        return
        
    out = interp1d(x_array, y_array, kind='linear')
    print(f"At X = {value}, ", f"{variable} =", out(value))
    return

probe_func_at(11.33)

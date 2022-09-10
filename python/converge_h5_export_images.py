"""
This script loads CONVERGE hdf5 data, applies a style sheet, and
exports images for each time step.

Usage:
    > python -O converge_h5_export_images.py

Necessary modules
-----------------
glob
    A module that can capture patterns and supports recursive wildcards
os
    A module that provides functions to interact with the operating system. It
    is installed with Python.
tecplot
    The PyTecplot package
    https://pypi.org/project/pytecplot/
tempfile
    A module for creating temporary files and directories. It is installed with
    Python.
time
    A module for timing information. It is installed with Python.


Description
-----------
This script runs in batch mode (unconnected with the Tecplot 360 GUI), and exports
a sequence of images.
Note that a style sheet needs to be applied to the data. You can create a style
sheet in the GUI by loading one data file, setting slice and iso-surfaces info,
and then going to Frame>Save frame style...

To capture memory utilized by PyTecplot, run this script with the memory profiler
(pypi.org/project/memory-profiler/) executable, this can be run as follows:
    > mprof run --include-children python -O converge_h5_export_images.py
"""

import glob
import os
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import tempfile
import time

start = time.time()
# Setting up the script to run in minimized memory mode
print("Minimize Memory")
tp.macro.execute_command('$!FileConfig LoadOnDemand{UnloadStrategy = MinimizeMemoryUse}')

# Getting the .h5 files and loading them into 360
base_dir = os.getcwd() # Note that the script and data files are in the same directory
files = glob.glob(os.path.join(base_dir,"post*.h5"))
now = time.time()
ds = tp.data.load_converge_hdf5(files)
print("Load time: ", time.time()-now)

# Applying a style sheet to the data
#  (Note that style sheets can be created in the GUI by loading one data file, setting slice and iso-surfaces info,
#  and then going to Frame>Save frame style...)
now = time.time()
tp.active_frame().load_stylesheet("converge_slice_iso.sty")
print("Style time: ", time.time()-now)

# Saving images for each time step to a directory (a temporary directory in this case)
now = time.time()
tmp_dir = tempfile.gettempdir()
print("Saving images to: ", tmp_dir)
tp.export.save_time_animation_png(os.path.join(tmp_dir, "out.png"), width=2048)
print("Anim time: ", time.time()-now)
print("Total time: ", time.time()-start)
print("Done")

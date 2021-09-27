"""
A script opening all files of a certain extension in a folder

General usage:
    > python -O .\open_multi_files_in_dir.py

Example usage with Linux batch mode:
    > /path/to/tecplot360/bin/tec360-env -- python -O .\open_multi_files_in_dir.py

Necessary modules
-----------------
sys
    A module that provides variables and functions to manipulate the Python runtime environment
glob
    A module that can capture patterns and supports recursive wildcards
os
    A module that provides functions to interact with the operating system


Description
-----------
This script can be used to loop through opening, plotting, and closing all the data files of a 
 particular file extension. This script can also be altered to append all the files in a directory
 to a single data set. Currently, it is written to open .szplt files (this can be updated by
 updating the load_tecplot_szl() and glob() functions).

To run this script in connected mode, we must first enable PyTecplot Connections via the
 Scripting menu (Scripting>PyTecplot Connections...).

Note, this script uses f-strings, so if you have a version of Python before 3.6,
 you may need to use str.format() instead.
"""
import tecplot as tp
import glob
import sys
import os

# This script will run in batch mode by default. Use the -c commandline argument for connected mode:
if '-c' in sys.argv:
    tp.session.connect()

# Create a new layout:
tp.new_layout()

# Load multiple files with the same extension from the following directory:
directory = r"path/to/datafiles"
# Or you can cd to the directory in the terminal with the data files, run the script and use the
# following to get the path of the current working directory:
#directory = os.getcwd()

# glob the files in that directory based on extension:
files = glob.glob(f"{directory}/*.szplt")

# Loop over the globbed files. These files can appended to one data set or
# opened individually with tp.new_layout()--the latter is demonstrated below:
for file in files:
    tp.new_layout()
    tp.data.load_tecplot_szl(file) #change this loader based on your needs
    print(f"Loaded: {file}")
    # ....
    # do something with the plot (set style, write data, export images,...)
    # ....
    # for example, show contour/slice and export an image:
    plot = tp.active_frame().plot()
    plot.contour(0).variable_index=2 #setting contour group 1 variable
    plot.show_contour=True
    plot.show_slices=True
    tp.export.save_png(f"{directory}/{os.path.basename(file)}.png") #saves the .png in the same dir as the data files

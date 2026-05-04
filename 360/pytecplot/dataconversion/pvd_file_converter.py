"""
This script runs in batch mode and converts PVD files via the vtk_file_converter handyscript
to Tecplot PLT format. This script will create one Tecplot PLT file per file referenced in
the PVD file.

Python modules needed:
----------------------
os
    A module that provides functions to interact with the operating system. It
    is installed with Python.
vtk_file_converter
    A Tecplot-created handy script that can be used as a module to convert readable VTK files into
    Tecplot PLT format. Note, all modules that are needed by the vtk_file_converter are also needed
    by this script. See vtk_file_converter.py for more details, URL:
    https://github.com/Tecplot/handyscripts/blob/master/python/dataconversion/vtk_file_converter.py
xml.dom.minidom
    A module utilized to parse XML formatting. It is a minimal implementation
    of the Document Object Model interface.

Example usage:
--------------
Windows:
    > python pvd_file_converter.py myfile.pvd

MacOS/Linux:
    > '/Applications/Tecplot 360 EX 2021 R2/bin/tec360-env' -- python3 pvd_file_converter.py myfile.pvd

"""
import os
import vtk_file_converter
import xml.dom.minidom

def convert_pvd_file(pvd_file, strand):
    dom = xml.dom.minidom.parse(pvd_file)
    collection = dom.getElementsByTagName("DataSet")
    for dataset in collection:
        t = dataset.getAttribute("timestep")
        fname = dataset.getAttribute("file")
        # Create an absolute path if needed
        if not os.path.exists(fname):
            fname = os.path.join(os.path.dirname(pvd_file), fname)
        if os.path.exists(fname):
            print("Converting: ", fname)
            plt_file = fname+".plt"
            vtk_file_converter.convert_vtk_file(fname, plt_file, strand, t)
            print("Saved to:   ", plt_file)
        else:
            print(fname, " does not exist")

if __name__ == '__main__':
    import argparse
    import glob
    parser = argparse.ArgumentParser(description="""Convert PVD file to Tecplot PLT format.
            A PVD file links to multiple other files. This script will create one Tecplot
            PLT file per file referenced in the PVD file.""")
    parser.add_argument("infile", help="PVD file to convert")
    args = parser.parse_args()
    files = glob.glob(args.infile)
    do_strands = True if len(files) > 1 else False
    for i,f in enumerate(files):
        print("Converting: ", f)
        strand = i+1 if do_strands else None
        convert_pvd_file(f, strand)

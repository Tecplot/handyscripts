import os
import xml.dom.minidom   
import vtk_file_converter

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
    parser = argparse.ArgumentParser(description="Convert PVD file to Tecplot PLT format. A PVD file links to multiple other files. This script will create one Tecplot PLT file per file referenced in the PVD file.")
    parser.add_argument("infile", help="PVD file to convert")
    args = parser.parse_args()
    files = glob.glob(args.infile)
    do_strands = True if len(files) > 1 else False
    for i,f in enumerate(files):
        print("Converting: ", f)
        strand = i+1 if do_strands else None
        convert_pvd_file(f, strand)

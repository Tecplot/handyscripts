import tecplot as tp
import glob
import sys
#
# Usage: 
#   mprof_to_plt.py mprofile.dat outfile.plt
#
#   On Linux, you may need to enclose wildcards in quotes:
#      mprof_to_plt.py 'mprofile*.dat' outfile.plt
#


def read_mprof_results(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        start_time = float(lines[1].split()[2])
        results = []
        for line in lines[1:]:
            vals = line.split()
            ram = float(vals[1])
            time = float(vals[2])-start_time
            results.append((ram,time))
        return results


tp.new_layout()
ds = tp.active_frame().dataset
ds.add_variable("Time")
ds.add_variable("RAM")

infiles = sys.argv[1]
outfile = sys.argv[2]

files = glob.glob(infiles)
for infile in files:
    print(infile)
    try:
        values = read_mprof_results(infile)
        zone = ds.add_ordered_zone(infile, shape=(len(values)))
        zone.values("RAM")[:] = [v[0] for v in values]
        zone.values("Time")[:] = [v[1] for v in values]
    except Exception as e:
        print("    Failure parsing file", e)
tp.data.save_tecplot_plt(outfile)
print("Saved to:", outfile)



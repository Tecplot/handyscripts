import tecplot as tp
import sys

infile = sys.argv[1]
outfile = sys.argv[2]

# Ensure we're starting from a clean slate
tp.new_layout()

# Read the binary file and write the ASCII file
tp.data.load_tecplot(infile)
print("Loaded file: ", infile)

tp.data.save_tecplot_ascii(outfile, precision=9)
print("ASCII file saved to: ", outfile)

import os
import tecplot

#{DOC:highlight}[
examples_dir = tecplot.session.tecplot_examples_directory()
#]
infile = os.path.join(examples_dir, 'SimpleData', 'F18.lay')

tecplot.load_layout(infile)
tecplot.export.save_png('load_example.png', 600, supersample=3)

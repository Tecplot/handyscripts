import os
import tecplot

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'F18.lay')

tecplot.load_layout(infile)
#{DOC:highlight}[
tecplot.save_layout('output.lpk')
#]
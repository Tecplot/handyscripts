from os import path
import tecplot
examples_directory = tecplot.session.tecplot_examples_directory()
infile = path.join(examples_directory,
                   'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(infile)
#{DOC:highlight}[
tecplot.data.save_tecplot_szl('wing.szplt')
#]
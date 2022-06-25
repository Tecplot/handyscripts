from os import path
import tecplot
examples_directory = tecplot.session.tecplot_examples_directory()
infile = path.join(examples_directory,
                   'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(infile)
variables_to_save = [dataset.variable(V)
                     for V in ('x','y','z','Pressure_Coefficient')]

zone_to_save = dataset.zone('WingSurface')
# write data out to an ascii file
#{DOC:highlight}[
tecplot.data.save_tecplot_ascii('wing.dat', dataset=dataset,
                                variables=variables_to_save,
                                zones=[zone_to_save])
#]
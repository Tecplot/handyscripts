from os import path
import tecplot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_directory = tecplot.session.tecplot_examples_directory()
infile = path.join(examples_directory, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(infile)

variables_to_save = [dataset.variable(V)
                     for V in ('x', 'y', 'z', 'Pressure_Coefficient')]

zone_to_save = [dataset.zone('WingSurface')]

# write data out to a binary PLT file
tecplot.data.save_tecplot_plt('wing.plt', dataset=dataset,
                              variables=variables_to_save,
                              zones=zone_to_save)

# write data out to an ascii file
tecplot.data.save_tecplot_ascii('wing.dat', dataset=dataset,
                                variables=variables_to_save,
                                zones=zone_to_save)

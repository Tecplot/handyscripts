import os
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import tecplot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()


examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D
frame.plot().show_contour = True

# ensure consistent output between interactive (connected) and batch
frame.plot().contour(0).levels.reset_to_nice()

# export image of wing
tecplot.export.save_png('wing.png', 600, supersample=3)

# extract an arbitrary slice from the surface data on the wing
extracted_slice = tecplot.data.extract.extract_slice(
    origin=(0, 0.25, 0),
    normal=(0, 1, 0),
    source=tecplot.constant.SliceSource.SurfaceZones,
    dataset=dataset)

extracted_slice.name = 'Quarter-chord C_p'

# get x from slice
extracted_x = extracted_slice.values('x')

# copy of data as a numpy array
x = extracted_x.as_numpy_array()

# normalize x
xc = (x - x.min()) / (x.max() - x.min())
extracted_x[:] = xc

# switch plot type in current frame
frame.plot_type = tecplot.constant.PlotType.XYLine
plot = frame.plot()

# clear plot
plot.delete_linemaps()

# create line plot from extracted zone data
cp_linemap = plot.add_linemap(
    name=extracted_slice.name,
    zone=extracted_slice,
    x=dataset.variable('x'),
    y=dataset.variable('Pressure_Coefficient'))

# integrate over the normalized extracted slice values
# notice we have to convert zero-based index to one-based for CFDAnalyzer
tecplot.macro.execute_extended_command('CFDAnalyzer4', '''
    Integrate
    VariableOption='Average'
    XOrigin=0 YOrigin=0
    ScalarVar={scalar_var}
    XVariable=1
'''.format(scalar_var=dataset.variable('Pressure_Coefficient').index + 1))

# get integral result from Frame's aux data
total = float(frame.aux_data['CFDA.INTEGRATION_TOTAL'])

# overlay result on plot in upper right corner
frame.add_text('integration result: {:.5f}'.format(total), (60,90))

# set style of linemap plot
cp_linemap.line.color = tecplot.constant.Color.Blue
cp_linemap.line.line_thickness = 0.8
cp_linemap.y_axis.reverse = True

# update axes limits to show data
plot.view.fit()

# export image of pressure coefficient as a function of x/c
tecplot.export.save_png('wing_pressure_coefficient.png', 600, supersample=3)

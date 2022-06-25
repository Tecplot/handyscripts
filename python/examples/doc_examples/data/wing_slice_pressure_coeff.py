import os
import tecplot as tp
from tecplot.constant import PlotType, SliceSource

examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing',
                        'OneraM6_SU2_RANS.plt')
dataset = tp.data.load_tecplot(datafile)

frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian3D

# set active plot to 3D and extract
# an arbitrary slice from the surface
# data on the wing
#{DOC:highlight}[
extracted_slice = tp.data.extract.extract_slice(
    origin=(0, 0.25, 0),
    normal=(0, 1, 0),
    source=SliceSource.SurfaceZones,
    dataset=dataset)
#]

# switch plot type in current frame, clear plot
plot = frame.plot(PlotType.XYLine)
plot.activate()
plot.delete_linemaps()

# create line plot from extracted zone data
cp_linemap = plot.add_linemap(
    name='Quarter-chord C_p',
    zone=extracted_slice,
    x=dataset.variable('x'),
    y=dataset.variable('Pressure_Coefficient'))

# set style of linemap plot and
# update axes limits to show data
cp_linemap.line.color = tp.constant.Color.Blue
cp_linemap.line.line_thickness = 0.8
cp_linemap.y_axis.reverse = True
plot.view.fit()

# export image of pressure coefficient as a function of x
tp.export.save_png('wing_slice_pressure_coeff.png', 600, supersample=3)

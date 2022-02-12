import os

import tecplot as tp
from tecplot.constant import *

examples_dir = tp.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
dataset = tp.data.load_tecplot(infile)

# Create a "blank" (zeroed-out) variable to use when plotting
# only one component of the (U, V, W) vectors
tp.data.operate.execute_equation(r'{blank} = 0')

# Setup the background frame and plot style
frame = tp.active_frame()
frame.background_color = Color.Black

plot = frame.plot(PlotType.Cartesian3D)
plot.activate()

contour = plot.contour(0)
contour.variable = dataset.variable('P(N/m2)')
contour.legend.show = False

plot.use_translucency = True
plot.show_contour = True
plot.show_edge = True
plot.axes.orientation_axis.color = Color.White
plot.view.width = 2.43

fmap = plot.fieldmap(0)
fmap.edge.edge_type = EdgeType.Creases
fmap.edge.color = Color.White
fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

#{DOC:highlight}[
frame_linking = plot.linking_between_frames
frame_linking.group = 1
frame_linking.link_view = True
frame_linking.link_frame_size_and_position = True
#]

def add_transparent_overlay(frame):
    '''Creates a transparent frame overlay with "blank" vector variables.'''
    overlay_frame = frame.page.add_frame()
    overlay_frame.transparent = True

    plot = overlay_frame.plot(frame.plot_type)
    plot.activate()
    plot.show_shade = False
    plot.axes.orientation_axis.show = False

    blank_var = overlay_frame.dataset.variable('blank')
    plot.vector.u_variable = blank_var
    plot.vector.v_variable = blank_var
    plot.vector.w_variable = blank_var
    plot.show_vector = True

    fmap = plot.fieldmap(0)
    fmap.vector.line_thickness = 0.35
    fmap.points.step = 80
    fmap.points.points_to_plot = PointsToPlot.AllCellCenters

    #{DOC:highlight}[
    frame_linking = plot.linking_between_frames
    frame_linking.group = 1
    frame_linking.link_view = True
    frame_linking.link_frame_size_and_position = True
    #]

    return plot

# Create three overlays - one for each vector component we want to show
u_plot = add_transparent_overlay(frame)
u_plot.vector.u_variable = dataset.variable('U(M/S)')
u_plot.fieldmap(0).vector.color = Color.Red

v_plot = add_transparent_overlay(frame)
v_plot.vector.v_variable = dataset.variable('V(M/S)')
v_plot.fieldmap(0).vector.color = Color.Green

w_plot = add_transparent_overlay(frame)
w_plot.vector.w_variable = dataset.variable('W(M/S)')
w_plot.fieldmap(0).vector.color = Color.Blue

#{DOC:highlight}[
# Now that all plots have been linked,
# movement in one will affect all three plots.
#]
u_plot.view.translate(x=5)

tp.export.save_png('plot3d_linking_between_frames.png')

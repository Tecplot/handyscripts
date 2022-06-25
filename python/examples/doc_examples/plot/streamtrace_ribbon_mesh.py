import os
import tecplot
from tecplot.constant import *

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'DownDraft.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D

plot = frame.plot()
plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
plot.show_mesh = False
plot.show_shade = False
plot.show_edge = True

plot.vector.u_variable_index = 4
plot.vector.v_variable_index = 5
plot.vector.w_variable_index = 6
plot.show_streamtraces = True

ribbon = plot.streamtraces.rod_ribbon
ribbon.width = .008
#{DOC:highlight}[
ribbon.mesh.show = True
ribbon.mesh.line_thickness = 0.2
#Ribbon mesh color inherited from streamtrace color
plot.streamtraces.color = Color.AquaGreen
#]

plot.streamtraces.add_rake(
    start_position=(0, 0.22, 0),
    end_position=(0, 0.22, 0.1),
    stream_type=Streamtrace.VolumeRibbon)

plot.view.width = 0.644
plot.view.alpha = 66.4
plot.view.theta = -122.4
plot.view.psi   = 124.5
plot.view.position = (5.3, 3.56, -4.3)

tecplot.export.save_png('streamtrace_ribbon_mesh.png', 600, supersample=3)


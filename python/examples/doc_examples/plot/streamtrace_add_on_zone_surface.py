import os

import tecplot
from tecplot.constant import *

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D

plot = frame.plot()

plot.vector.u_variable_index = 4
plot.vector.v_variable_index = 5
plot.vector.w_variable_index = 6
plot.show_streamtraces = True

plot.streamtraces.add_on_zone_surface(
            # To add streamtraces to the currently active zones,
            # pass zones=None
            zones=[1],  # Add streamtraces on 2nd zone only
            stream_type=Streamtrace.SurfaceLine,
            num_seed_points=200)

tecplot.export.save_png('streamtrace_add_on_zone_surface.png', 600, supersample=3)

'''
This script shows how to do the following:
    1) Open a data file
    2) Use execute_equation() to calculate new variables which
       are the difference between two time steps
    3) Create a new frame and setup frame styles
    4) Export images for each time step.
'''
import time

import tecplot as tp
from tecplot.constant import *

now = time.time()

# Run this script with '-c' to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   'Scripting' -> 'PyTecplot Connections...' -> 'Accept connections'
import sys
if '-c' in sys.argv:
    tp.session.connect()

def calculate_delta(var_list, z1, z2):
    for v in var_list:
        var_name = f'{v.name}_Delta'
        if var_name not in z1.dataset.variable_names:
            z1.dataset.add_variable(var_name)

        use_equations = True
        if use_equations:
            # Use 360's equation processing to do the math
            equation = '{{{name}_Delta}} = V{var} - V{var}[{zone}]'.format(
                name=v.name, var=v.index + 1, zone=z1.index + 1)
            print(equation)
            tp.data.operate.execute_equation(equation, zones=[z2])
        else:
            # Use numpy to do the math.  This will be slower when running 'connected'
            # due to additional overhead to pull the data values out of the 360 engine
            # into Python and then stuff them back into the engine.  In batch mode this
            # takes about the same amount of time.
            z1_vals = z1.values(v)[:]
            z2_vals = z2.values(v)[:]
            print(f'Computing delta of {v.name} between {z1.name} and {z2.name}')
            z2.values(var_name)[:] = z2_vals-z1_vals

# Open the transient data file and acquire a handle to the dataset
tp.new_layout()
examples_dir = tp.session.tecplot_examples_directory()
datafile = examples_dir / 'SimpleData/VortexShedding.plt'
dataset = tp.data.load_tecplot(datafile)

# tecplot.session.suspend() can improve performance in batch and connected modes.
# The effect will be greater in connected mode as it prevents the 360 GUI from
# updating as the script is running
with tp.session.suspend():
    variable_list = [dataset.variable('P(N/M2)')]

    # Calculate the delta between two zones at different time steps.
    for z in range(0, dataset.num_zones-1):
        calculate_delta(variable_list, dataset.zone(z), dataset.zone(z+1))

    # Get a handle to the current frame and create a new frame
    frame1 = tp.active_frame()
    frame2 = tp.active_page().add_frame()
    frame2.plot_type = tp.constant.PlotType.Cartesian2D

    tp.active_page().tile_frames(TileMode.Columns)

    # Ensure frame is activated before setting its style.
    frame1.activate()
    plot1 = frame1.plot()
    plot1.show_contour = True
    plot1.contour(0).variable = dataset.variable('P(N/M2)')
    plot1.contour(0).levels.reset_to_nice()
    tp.macro.execute_command('''
        $!LINKING BETWEENFRAMES{LINKSOLUTIONTIME = YES}
        $!LINKING BETWEENFRAMES{LINKXAXISRANGE = YES}
        $!LINKING BETWEENFRAMES{LINKYAXISRANGE = YES}
        $!PROPAGATELINKING
          LINKTYPE = BETWEENFRAMES
          FRAMECOLLECTION = ALL
    ''')

    # Ensure frame2 is active before setting its style
    frame2.activate()
    plot2 = frame2.plot()
    plot2.contour(0).variable = dataset.variable('P(N/M2)_Delta')
    plot2.show_contour = True
    plot2.contour(0).levels.reset(num_levels=11)
    plot2.contour(0).colormap_name = 'Diverging - Blue/Red'

    plot2.axes.x_axis.max = 0.04
    plot2.axes.x_axis.min = -0.007
    plot2.axes.y_axis.max = 0.01
    plot2.axes.y_axis.min = -0.01

    # Iterate over a few solution times and export
    # an image for each. Note that frame2 is still
    # the active frame and is the one that will be
    # exported.
    for t in plot2.solution_times[1:4]:
        plot2.solution_time = t
        tp.export.save_png(f'timestepdelta_{t:.6f}.png', 600, supersample=3)

    # Save a data file to retain the results
    vars_to_save = [
        dataset.variable('X(M)'),
        dataset.variable('Y(M)'),
        dataset.variable('P(N/M2)'),
        dataset.variable('P(N/M2)_Delta'),
    ]
    tp.data.save_tecplot_plt('output.plt', variables=vars_to_save)

print('Elapsed:', time.time()-now)

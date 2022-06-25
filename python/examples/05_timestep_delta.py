"""
This script shows how to do the following:
    1) Open a layout file
    2) Use execute_equation() to calculate new variables which
       are the difference between two time steps
    3) Create a new frame and setup frame styles
    4) Export images for each time step.
"""
import tecplot as tp
from os import path

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# Open the transient layout and acquire a handle to the dataset
examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
dataset = tp.data.load_tecplot(datafile)

def create_delta_variables(var_list):
    for v in var_list:
        equation = '{{{}_Delta}} = 0'.format(dataset.variable(v).name)
        tp.data.operate.execute_equation(equation)

def calculate_delta(var_list, z1, z2):
    for v in var_list:
        equation = '{{{name}_Delta}} = V{var} - V{var}[{zone}]'.format(
            name=dataset.variable(v).name, var=v + 1, zone=z1.index + 1)
        tp.data.operate.execute_equation(equation, zones=[z2])

with tp.session.suspend():
    variable_list = range(2, dataset.num_variables)
    create_delta_variables(variable_list)

    # Now we actually calculate the delta between two zones at different time steps.
    for z in range(0, dataset.num_zones-1):
        calculate_delta(variable_list, dataset.zone(z), dataset.zone(z+1))

# Get a handle to the current frame and create a new frame
frame1 = tp.active_frame()
frame2 = tp.active_page().add_frame()
frame2.plot_type = tp.constant.PlotType.Cartesian2D

# Ensure frame is activated before setting its style.
# In future versions of PyTecplot
# there will by Python APIs which replace the tp.macro.execute_command() calls
frame1.activate()
plot1 = frame1.plot()
plot1.show_contour = True
plot1.contour(0).variable = dataset.variable("P(N/M2)")
plot1.contour(0).levels.reset_to_nice()
tp.macro.execute_command("""
    $!LINKING BETWEENFRAMES{LINKSOLUTIONTIME = YES}
    $!LINKING BETWEENFRAMES{LINKXAXISRANGE = YES}
    $!LINKING BETWEENFRAMES{LINKYAXISRANGE = YES}
    $!PROPAGATELINKING
      LINKTYPE = BETWEENFRAMES
      FRAMECOLLECTION = ALL""")

# Ensure frame2 is active before setting its style
frame2.activate()
plot2 = frame2.plot()
plot2.contour(0).variable = dataset.variable("P(N/M2)_Delta")
plot2.show_contour = True
plot2.contour(0).levels.reset(num_levels=11)
plot2.contour(0).colormap_name = 'Diverging - Blue/Red'

plot2.axes.y_axis.min = -0.02
plot2.axes.y_axis.max = 0.02
plot2.axes.x_axis.min = -0.008
plot2.axes.x_axis.max = 0.04

# Iterate over the solution times and export
# an image for each solution time.
# Note that frame2 is still the active frame
# and is the one that will be exported.
for time in plot2.solution_times[1:4]:
    plot2.solution_time = time
    tp.export.save_png(r'timestepdelta_{:.6f}.png'.format(time), 600,
                       supersample=3)

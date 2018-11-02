import tecplot as tp
from tecplot.exception import *
import tputils
import tpmath
import time

tp.session.connect()

plot = tp.active_frame().plot()
dataset = tp.active_frame().dataset
# Must use a list, because we use this twice - the generator is empty the second time around
variables_to_average = list(dataset.variables())
constant_variables = None
# If you're only interested in a subset of variables, you can supply them like this
##variables_to_average = [dataset.variable("Pressure Coefficient")]
# Variables which are known to be constant can be supplied here - saving computation time
##constant_variables = [plot.axes.x_axis.variable, plot.axes.y_axis.variable, plot.axes.z_axis.variable]

start = time.time()
with tp.session.suspend():
    dataset = tp.active_frame().dataset

    now = time.time()
    # This function is really slow for large numbers of zones. We will
    # work on improving the performance in a future release.
    zones_by_strand = tputils.get_zones_by_strand(dataset)
    print("Time to get zones by strand: ", time.time()-now)

    for strand, source_zones in zones_by_strand.items():
        # Compute the average for the source zones
        now = time.time()
        avg_zone = tpmath.compute_average(source_zones, variables_to_average, constant_variables)
        print("Time to compute average for strand {}: {}".format(strand, time.time()-now))
        print("AvgZone is: ", avg_zone.name)

        # Create Delta variables for each variable we averaged. The resulting Delta variable
        # is created for each source zone.
        now = time.time()
        for v in variables_to_average:
            delta_var_name = "{}_Delta_from_Avg".format(v.name)
            eqn = '{%s} = {%s} - {%s}[%d]'%(delta_var_name, v.name, v.name, avg_zone.index+1)
            print(eqn)
            tp.data.operate.execute_equation(equation=eqn, zones=source_zones)  
        print("Time to compute time deltas for strand {}: {}".format(strand, time.time()-now))
print("Total Execution Time: {}".format(time.time()-start))

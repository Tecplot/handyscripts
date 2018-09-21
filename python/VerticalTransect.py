import time
import numpy as np
import tecplot as tp
from tecplot.constant import *
import tputils

tp.session.connect()

def get_first_zone_in_strand(strand, dataset):
    for z in dataset.zones():
        if z.strand == strand:
            return z
    return None
    
def plot_vertical_transect(zone, xvar, yvar):
    frame = tp.active_page().add_frame()
    tputils.attach_dataset(frame, zone.dataset)
    plot = frame.plot(PlotType.Cartesian2D)
    plot.activate()
    fmap = plot.fieldmap(zone)
    for f in plot.fieldmaps():
        f.show = False
    fmap.show = True
    plot.show_mesh=False
    plot.show_shade=False
    # Need to assign a contour variable before we can turn on the contour layer
    plot.contour(0).variable_index=5 # FVCOM data, the first 5 variables are spatial
    plot.show_contour=True
    plot.show_scatter=False
    plot.axes.x_axis.variable = xvar
    plot.axes.y_axis.variable = yvar
    plot.axes.axis_mode=AxisMode.Independent
    # Fit the data first to get the ranges reasonable, then fine tune
    plot.view.fit()
    x_minmax = tputils.fieldmap_minmax(fmap, xvar)
    y_minmax = tputils.fieldmap_minmax(fmap, yvar)
    plot.axes.x_axis.min = x_minmax[0]
    plot.axes.x_axis.max = x_minmax[1]
    plot.axes.y_axis.min = y_minmax[0]
    plot.axes.y_axis.max = y_minmax[1]
    tp.macro.execute_command('$!Linking BetweenFrames{LinkSolutionTime = Yes}')
    tp.macro.execute_command('''$!PropagateLinking 
      LinkType = BetweenFrames
      FrameCollection = All''')
    tp.macro.execute_extended_command(command_processor_id='Multi Frame Manager',
        command='TILEFRAMESHORIZ')
    return plot

def make_transect_zone(x_vals, y_vals, source_strand, dataset):
    try:
        dist_var = dataset.variable("distance")
    except:
        dist_var = dataset.add_variable("distance")
    dd = np.sqrt((x_vals[1:] - x_vals[:-1])**2 + (y_vals[1:] - y_vals[:-1])**2)
    dist = np.cumsum(dd)
    dist = np.concatenate([[0],dist])
    
    siglev_vals = np.unique(get_first_zone_in_strand(source_strand, dataset).values("siglev").as_numpy_array())

    iMax = len(x_vals)
    jMax = len(siglev_vals)

    X, Z = np.meshgrid(x_vals, siglev_vals)
    Y, Z = np.meshgrid(y_vals, siglev_vals)
    D, Z = np.meshgrid(dist, siglev_vals)
    
    zone_name = "Transect"
    result = dataset.add_ordered_zone(zone_name, (iMax,jMax,1),locations=[ValueLocation.Nodal]*dataset.num_variables)
    result.values("x")[:] = X
    result.values("y")[:] = Y
    result.values("distance")[:] = D
    result.values("siglev")[:] = Z
    return result


# If you have a specific set of XY points, simply updated this function to supply a different 
# set of values.  This function looks for a zone called Extracted Points and uses the XY values
# from that zone.  You could also open a file and use XY points from a CSV file here
def get_xy_points(dataset):
    transect_points_zone = dataset.zone("Extracted Points")
    x_vals = transect_points_zone.values("X").as_numpy_array()
    y_vals = transect_points_zone.values("Y").as_numpy_array()
    return x_vals,y_vals


def main():
    frame = tp.active_frame()
    threed_plot = tp.active_frame().plot(PlotType.Cartesian3D)
    dataset = tp.active_frame().dataset

    # FVCOM volume data should be strand #1
    source_strand = 1
    source_zones = [z for z in dataset.zones() if z.strand == source_strand]
    solution_time_to_zone = dict()
    for z in source_zones:
        solution_time_to_zone[z.solution_time] = z

    # This will interpolate nearly all the variables in the dataset.  If you're
    # only interested in a couple variables, then you can modify this list. This will
    # speed up the process, but could lead to confusing results since the vertical profile
    # will have "uninterpolated" values for any unspecified variables.  Buyer beware.
    variables_to_interpolate = list(dataset.variables())
    variables_to_interpolate.remove(dataset.variable("x"))
    variables_to_interpolate.remove(dataset.variable("y"))
    variables_to_interpolate.remove(dataset.variable("siglev"))
    # Might not be in the dataset yet
    try:
        variables_to_interpolate.remove(dataset.variable("distance"))
    except:
        pass

    begin = time.time()
    transect_base_zone = None
    orig_z_axis = threed_plot.axes.z_axis.variable

    # Save off the current view of the 3D frame and then set the Z-axis to siglev
    # so we can to a proper linear interpolation
    tp.macro.execute_command("$!View Copy")
    threed_plot.axes.z_axis.variable = dataset.variable("siglev")


    # For each time step we create an IJ ordered zone with XY points defined by x_vals & y_vals. The
    # z-values are the unique 'siglev' values.  We then interpolate from the volume data to this
    # IJ-ordered zone to create the transect.
    #
    # You must have enough XY points to capture the grid resolution of the volume dataset.
    x_vals,y_vals = get_xy_points(dataset)
    new_strand = tputils.max_strand(dataset) + 1

    for t in dataset.solution_times:
        start = time.time()
        if not transect_base_zone: 
            transect_base_zone = make_transect_zone(x_vals, y_vals, source_strand, dataset)
            transect_base_zone.strand = new_strand
            transect_zone = transect_base_zone
        else:
            transect_zone = dataset.copy_zones([transect_base_zone])[0]
        transect_zone.solution_time = t
        source_zone = solution_time_to_zone[t]
        tp.data.operate.interpolate_linear(transect_zone, source_zones=source_zone, variables=variables_to_interpolate)
        print("Transect at t=%f complete: "%(t), time.time()-start)

    # Restore the 3D plot to its original view
    threed_plot.axes.z_axis.variable = orig_z_axis

    # Plot the results
    transect_plot = plot_vertical_transect(transect_base_zone, dataset.variable("distance"), dataset.variable("z"))

    # Set the contour color to match the 3D plot
    cont_group = threed_plot.fieldmap(source_zones[0]).contour.flood_contour_group_index
    transect_plot.contour(cont_group).variable_index = threed_plot.contour(cont_group).variable_index
    transect_plot.contour(cont_group).colormap_name=threed_plot.contour(cont_group).colormap_name
    transect_plot.fieldmap(transect_base_zone).contour.flood_contour_group_index = cont_group
    transect_plot.contour(cont_group).levels.reset_levels(*threed_plot.contour(cont_group).levels)

    frame.activate()
    tp.macro.execute_command("$!View Paste")

    print("Total time: ", time.time()-begin)

with tp.session.suspend():
    main()

"""Create a vertical profile over time for the active contour of a 3D plot.

usage:
General:
    > python VerticalProfile.py [args]

usage example:
    > python .\VerticalProfile.py -x 78.2 -y -50.66

Necessary modules
-----------------
time
    A module with generic time abilities
tputils
    Generic PyTecplot utilities supplied by the Tecplot GitHub handyscripts

Description
-----------
Creates a single vertical profile for non time-dependent data. Creates a vertical profile over time for time-dependent data.
Note the X and Y inputs are not necessarily the X and Y variables but rather the X and Y axis variables. If no args are supplied,
the user will be prompted to add X and Y arguments. The Vertical Profile will be taken of the flood variable of the first fieldmap.
See the source_fieldmap variable to change functionality.
This script must be run in connected mode to function properly.

"""
import time
import tecplot as tp
from tecplot.constant import *
import tputils


def extract_vertical_line(x, y, source_fieldmap, plot):
    '''Extracts a vertical line by creating a slice of a slice at the given X, Y locations.'''
    tp.macro.execute_command("$!ActiveFieldMaps = [{}]".format(source_fieldmap + 1))
    x_slice = tp.data.extract.extract_slice(
        origin=(x, 0, 0),
        normal=(1, 0, 0),
        source=SliceSource.VolumeZones)
    tp.macro.execute_command("$!ActiveFieldMaps = [{}]".format(plot.fieldmap(x_slice).index + 1))
    result = tp.data.extract.extract_slice(
        origin=(0, y, 0),
        normal=(0, 1, 0),
        source=SliceSource.SurfaceZones)
    x_slice.dataset.delete_zones(x_slice)
    return result


def plot_vertical_profile(zone, xvar, yvar):
    '''Plots the vertical profile on a separate frame.'''
    frame = tp.active_page().add_frame()
    tputils.attach_dataset(frame, zone.dataset)
    plot = frame.plot(PlotType.Cartesian2D)
    plot.activate()
    fmap = plot.fieldmap(zone)
    for f in plot.fieldmaps():
        f.show = False
    fmap.show = True
    plot.show_mesh = True
    plot.show_shade = False
    plot.show_contour = False
    plot.show_scatter = True
    fmap.scatter.symbol().shape = GeomShape.Circle
    plot.axes.x_axis.variable = xvar
    plot.axes.y_axis.variable = yvar
    plot.axes.axis_mode = AxisMode.Independent
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
    # Uncomment below to force tiled frames. Otherwise the new frame will overlay the 3D plot.
    # tp.macro.execute_extended_command(command_processor_id='Multi Frame Manager',
    #                                   command='TILEFRAMESVERT')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Create a Vertical Profile of an active Tecplot Session")
    parser.add_argument("-x", help="X location of the vertical profile", type=float)
    parser.add_argument("-y", help="Y location of the vertical profile", type=float)
    args = parser.parse_args()

    tp.session.connect()
    frame = tp.active_frame()
    threed_plot = tp.active_frame().plot(PlotType.Cartesian3D)
    threed_plot.show_contour = True
    dataset = frame.dataset
    active_fieldmap_indices = threed_plot.active_fieldmap_indices
    source_fieldmap = 0
    new_strand = tputils.max_strand(dataset) + 1

    # Argument handling for X and Y variables. Prompts user if variables are not supplied.
    if args.x is not None:
        x = args.x
    else:
        x = float(input("Enter x location: "))
    if args.y is not None:
        y = args.y
    else:
        y = float(input("Enter y location: "))

    with tp.session.suspend():
        # Check if data is time-dependent
        if dataset.solution_times:
            # Data with solution times will create a vertical profile for each timestep.
            for t in dataset.solution_times:
                start = time.time()
                threed_plot.solution_time = t
                result = extract_vertical_line(x, y, source_fieldmap, threed_plot)
                result.strand = new_strand
                result.solution_time = t
                print("Made vertical profile for t={} in {} seconds".format(t, time.time() - start))
        else:
            # Data with no solution times will still create a single vertical profile.
            start = time.time()
            result = extract_vertical_line(x, y, source_fieldmap, threed_plot)
            print("Made a single vertical profile in {} seconds".format(time.time() - start))

        threed_plot.active_fieldmap_indices = active_fieldmap_indices

        xvar = threed_plot.fieldmap(source_fieldmap).contour.flood_contour_group.variable
        yvar = threed_plot.axes.z_axis.variable
        plot_vertical_profile(result, xvar, yvar)

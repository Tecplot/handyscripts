import time
import tecplot as tp
from tecplot.constant import *
import tputils

tp.session.connect()


def extract_vertical_line(x, y, source_fieldmap, plot):
    tp.macro.execute_command("$!ActiveFieldMaps = [{}]".format(source_fieldmap))
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
    # tp.macro.execute_extended_command(command_processor_id='Multi Frame Manager',
    #    command='TILEFRAMESVERT')


frame = tp.active_frame()
threed_plot = tp.active_frame().plot(PlotType.Cartesian3D)
dataset = tp.active_frame().dataset
active_fieldmap_indices = threed_plot.active_fieldmap_indices

source_fieldmap = 1
new_strand = tputils.max_strand(dataset) + 1

x = float(input("Enter x location: "))
y = float(input("Enter y location: "))

with tp.session.suspend():
    for t in dataset.solution_times:
        start = time.time()
        threed_plot.solution_time = t
        result = extract_vertical_line(x, y, source_fieldmap, threed_plot)
        result.strand = new_strand
        result.solution_time = t
        print("Made vertical profile for t={} in {} seconds".format(t, time.time() - start))

    threed_plot.active_fieldmap_indices = active_fieldmap_indices

    xvar = threed_plot.fieldmap(source_fieldmap).contour.flood_contour_group.variable
    yvar = threed_plot.axes.z_axis.variable
    plot_vertical_profile(result, xvar, yvar)

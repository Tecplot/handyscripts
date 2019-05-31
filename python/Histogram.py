import tecplot as tp
import numpy as np
from tecplot.constant import *



def plot_histogram(histogram, var_name):
    bins = histogram[0]
    edges = histogram[1]

    # Create a new frame and dataset to hold the histogram results
    frame = tp.active_page().add_frame()
    ds = frame.create_dataset("Histogram of "+var_name, [var_name, "Counts"])
    frame.name = "Histogram of {}".format(var_name)

    # Create a FE-Quad zone, where each cell represents a bin
    zone = ds.add_fe_zone(ZoneType.FEQuad, "Histogram of "+var_name, 4*len(bins), len(bins))
    xvals = []
    yvals = []
    connectivity = []
    for i,count in enumerate(bins):
        xvals.extend([edges[i], edges[i+1], edges[i+1], edges[i]])
        yvals.extend([0,0,count,count])
        connectivity.append([i*4, i*4+1, i*4+2, i*4+3])
    zone.values(0)[:] = xvals
    zone.values(1)[:] = yvals
    zone.nodemap[:] = connectivity

    # Setup the plot style to present the results
    plot = frame.plot(tp.constant.PlotType.Cartesian2D)
    plot.activate()
    plot.axes.axis_mode = tp.constant.AxisMode.Independent
    plot.view.fit()
    x_axis = plot.axes.x_axis
    x_axis.ticks.auto_spacing = False
    x_axis.ticks.spacing_anchor = edges[0]
    x_axis.ticks.spacing = abs(edges[1] - edges[0])
    plot.show_mesh = True
    plot.show_shade = True

    # There will only be one fieldmap...
    for fmap in plot.fieldmaps():
        fmap.shade.color = tp.constant.Color.Red

    plot.axes.y_axis.title.offset = 10 
    plot.axes.y_axis.title.show = True
    plot.axes.x_axis.title.show = True
    plot.axes.x_axis.title.offset = 10 

    plot.axes.x_axis.tick_labels.offset = 1.5
    plot.axes.x_axis.tick_labels.angle = 35
    plot.axes.x_axis.tick_labels.show = True
    plot.axes.x_axis.ticks.minor_num_ticks = 0

    # Reduce the viewport make room for the axis titles
    plot.axes.viewport.bottom=15
    plot.axes.viewport.left=16

    return plot

def hist(var, bins = 5, zones = None):
    if not zones:
        zones = var.dataset.zones()
    zones = list(zones)
    all_values = np.array([])
    for z in zones:
        values = z.values(var).as_numpy_array()
        all_values = np.append(all_values, values)
    h = np.histogram(all_values, bins)
    return h

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Computes and plots a histogram of a given variable.")
    parser.add_argument("varname", help="Name of the variable for which to compute the histogram")
    parser.add_argument("bins", help="Number of bins in the histogram", type=int)
    args = parser.parse_args()
    tp.session.connect()
    with tp.session.suspend():
        dataset = tp.active_frame().dataset
        var_name = args.varname
        variable = dataset.variable(var_name)
        bins = args.bins
        zones = dataset.zones()
        h = hist(variable, bins, zones)
        plot = plot_histogram(h, variable.name)


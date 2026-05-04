from collections.abc import Iterable
import itertools as it

import tecplot as tp
from tecplot.constant import AxisMode, Color, PlotType, SurfacesToPlot


def plot_filled_lines_3d(x, *yy, z=(-0.2, 0.2), y0=0, colors=None,
                         name='Line Data', page=None):
    """Plot a series of lines in (x, y) as 3D volumes.

    Parameters:
        x (array): Values along the x-axis
        *yy (arrays): One or more arrays of y-values for each x value. These
            must be the same length as ``x``.
        z (2-tuple): (min, max) around the z-coordinate for each line.
        y0 (float): Base y-value.
        colors (tecplot.plot.ContourGroup or array of Colors): The contour
            group will color each line using the full range if given.
            Otherwise, colors obtained from the enumeration
            ``tecplot.constant.Color`` will be cycled through for each line.
            The first contour group of the plot will be used by default.
        name (str): Name of the frame that will be fetched or created. Also
            used to fetch or create zones by name. Any other zones that start
            with this string will be deleted from the dataset.
        page (tecplot.layout.Page): Page on which to add or get the frame. The
            active page will be used by default.

    Example plotting some Legedre polynomials::

        import numpy as np
        from numpy.polynomial import legendre

        import tecplot as tp

        x = np.linspace(-1., 1., 100)
        yy = [legendre.Legendre(([0] * i) + [1])(x) for i in range(1, 6)]
        plot = plot_filled_lines_3d(x, *yy, y0=-1.)
        tp.save_png('line_data.png')
    """
    if page is None:
        page = tp.active_page()

    # get or create a frame with the given name
    frame = page.frame(name)
    if frame is None:
        frame = page.add_frame()
        frame.name = name

    # use existing dataset on frame or create it
    if frame.has_dataset:
        ds = frame.dataset
        vnames = ds.variable_names
        for vname in ['x', 'y', 'z', 's']:
            if vname not in vnames:
                ds.add_variable(vname)
    else:
        ds = frame.create_dataset(name, ['x', 'y', 'z', 's'])

    # create or modify zones named "{name} {i}" based on the values in yy
    x = np.asarray(x, dtype=float)
    for i, y in enumerate(yy):
        shape = (len(x), 2, 2)
        zname = '{name} {i}'.format(name=name, i=i)
        zn = ds.zone(zname)

        # recreate zone if shape has changed
        if zn is None or zn.dimensions != shape:
            new_zn = ds.add_ordered_zone(zname, shape)
            if zn:
                ds.delete_zones(zn)
            zn = new_zn

        # prepare arrays to be pushed into tecplot
        y1 = np.array([float(y0), 1.])
        z1 = np.asarray(z, dtype=float) + i
        Z, Y, X = np.meshgrid(z1, y1, x, indexing='ij')
        Y[:,1,:] = y

        # fill zone with data
        zn.values('x')[:] = X
        zn.values('y')[:] = Y
        zn.values('z')[:] = Z
        zn.values('s')[:] = np.full(Z.size, i / ((len(yy) - 1) or 1))

    # remove any extra zones from a previous run
    zones_to_delete = []
    while True:
        i = i + 1
        zn = ds.zone('{name} {i}'.format(name=name, i=i))
        if zn is None:
            break
        zones_to_delete.append(zn)
    if zones_to_delete:
        ds.delete_zones(*zones_to_delete)

    # adjust plot to show the line zones
    plot = frame.plot(PlotType.Cartesian3D)
    plot.activate()

    # set axes variables, contour variable, hide legend
    plot.axes.x_axis.variable = ds.variable('x')
    plot.axes.y_axis.variable = ds.variable('y')
    plot.axes.z_axis.variable = ds.variable('z')

    if isinstance(colors, Iterable):
        # color each zone by shade color
        plot.show_contour = False
        plot.show_shade = True
        for zn, col in zip(ds.zones(name + ' *'), it.cycle(colors)):
            plot.fieldmap(zn).shade.color = Color(col)
    else:
        # color each zone by contour values over the whole contour range
        if colors is None:
            contour = plot.contour(0)
        plot.show_contour = True
        plot.show_shade = False
        contour.variable = ds.variable('s')
        contour.legend.show = False
        contour.levels.reset_levels(np.linspace(0, 1, 256))

    # turn on axes, contour and translucency. hide orientation axes
    plot.axes.x_axis.show = True
    plot.axes.y_axis.show = True
    plot.axes.z_axis.show = True
    plot.use_translucency = True
    plot.axes.orientation_axis.show = False

    # turn on surfaces and adjust translucency
    for zn in ds.zones('Line Data*'):
        fmap = plot.fieldmap(zn)
        fmap.show = True
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        fmap.effects.surface_translucency = 50

    # set the view
    plot.view.psi = 0
    plot.view.theta = 0
    plot.view.alpha = 0
    plot.view.rotate_axes(20, (1, 0, 0))
    plot.view.rotate_axes(-20, (0, 1, 0))

    # set axes limits
    ax = plot.axes
    ax.axis_mode = AxisMode.Independent
    ax.x_axis.min = min(x)
    ax.x_axis.max = max(x)
    ax.y_axis.min = y0
    ax.y_axis.max = 1.05 * ds.variable('y').max()
    ax.z_axis.min = z[0]
    ax.z_axis.max = z[1] + (len(yy) - 1)

    # adjust tick spacing for z-axis
    ax.z_axis.ticks.auto_spacing = False
    ax.z_axis.ticks.spacing = 1

    # fit the view and then zoom out slightly
    plot.view.fit()
    plot.view.width *= 1.05

    return plot


if __name__ == '__main__':
    import sys
    import numpy as np
    from numpy import polynomial as poly

    from tecplot.constant import Color

    if '-c' in sys.argv:
        tp.session.connect()

    # some sample data (orthogonal polynomial series)
    x = np.linspace(-1., 1., 100)
    yy = [poly.legendre.Legendre(([0] * i) + [1])(x)
          for i in range(1, 6)]

    # use tecplot color palette to shade each line
    # alternatively, set colors to None to use the
    # plot's contour color values.
    colors = [Color(i + 1) for i in range(len(yy))]
    plot = plot_filled_lines_3d(x, *yy, y0=-1, colors=colors)

    if '-c' not in sys.argv:
        tp.save_png('line_data.png')

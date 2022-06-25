import atexit, os, multiprocessing, sys

import tecplot as tp


def init(datafile, stylesheet):
    # !!! IMPORTANT !!!
    # Must register stop at exit to ensure Tecplot cleans
    # up all temporary files and does not create a core dump
    atexit.register(tp.session.stop)

    # Load data and apply a style sheet - done only once for all workers
    tp.data.load_tecplot(datafile)
    tp.active_frame().load_stylesheet(stylesheet)


def work(solution_time):
    # Set the solution time, save the image and return the maximum pressure
    frame = tp.active_frame()
    frame.plot().solution_time = solution_time
    tp.export.save_png('img{0:.8f}.png'.format(solution_time))
    return frame.dataset.variable('P(N/M2)').max()


def process_pool_map(func, args, **kwargs):
    # !!! IMPORTANT !!!
    # On Linux systems, Python's multiprocessing start method
    # defaults to "fork" which is incompatible with PyTecplot
    # and must be set to "spawn"
    multiprocessing.set_start_method('spawn')

    # Set up the pool with initializing function and associated arguments
    num_workers = min(multiprocessing.cpu_count(), len(args))
    pool = multiprocessing.Pool(num_workers, **kwargs)

    try:
        # Map the work function to each of the job arguments
        result = pool.map(work, args)
    finally:
        # !!! IMPORTANT !!!
        # Must join the process pool before parent script exits
        # to ensure Tecplot cleans up all temporary files
        # and does not create a core dump
        pool.close()
        pool.join()

    return result


def plot_line(x, y, xlabel='x', ylabel='y'):
    # Create a new frame and plot (x, y)
    with tp.session.suspend():
        frame = tp.active_page().add_frame()
        dataset = frame.create_dataset('Dataset', [xlabel, ylabel])
        zone = dataset.add_ordered_zone('Zone', len(x))
        zone.values(xlabel)[:] = x
        zone.values(ylabel)[:] = y

    plot = frame.plot(tp.constant.PlotType.XYLine)
    plot.activate()
    return frame, plot


if __name__ == '__main__':
    if sys.version_info < (3, 5):
        raise Exception('This example requires Python version 3.5+')
    if tp.session.connected():
        raise Exception('This example must be run in batch mode')

    # Get the datafile, stylesheet and job parameters (solution times)
    examples_dir = tp.session.tecplot_examples_directory()
    datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
    stylesheet = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.sty')

    # for this example, we are only processing the first MAXJOBS solution times
    MAXJOBS = 4
    solution_times = list(tp.data.load_tecplot(datafile).solution_times)[:MAXJOBS]

    pmax = process_pool_map(work, solution_times,
                            initializer=init,
                            initargs=(datafile, stylesheet))

    # Plot results and save to image file
    frame, plot = plot_line(x=solution_times, y=pmax,
                            xlabel='Time (s)', ylabel='Max Pressure (N/m^2)')

    # Adjust plot style
    lmap = plot.linemap(0)
    lmap.line.line_thickness = 0.8
    lmap.y_axis.title.offset += 6
    plot.axes.viewport.left += 5

    # Save image of just the frame created by plot_line()
    tp.export.save_png('pressure_range_over_time.png', region=frame)

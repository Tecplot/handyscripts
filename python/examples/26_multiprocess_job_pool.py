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
    # set solution time and save off image
    tp.active_frame().plot().solution_time = solution_time
    tp.export.save_png('img{0:.8f}.png'.format(solution_time))


if __name__ == '__main__':
    if sys.version_info < (3, 5):
        raise Exception('This example requires Python version 3.5+')
    if tp.session.connected():
        raise Exception('This example must be run in batch mode')

    # !!! IMPORTANT !!!
    # On Linux systems, Python's multiprocessing start method
    # defaults to "fork" which is incompatible with PyTecplot
    # and must be set to "spawn"
    multiprocessing.set_start_method('spawn')

    # Get the datafile, stylesheet and job parameters (solution times)
    examples_dir = tp.session.tecplot_examples_directory()
    datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
    stylesheet = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.sty')

    # for this example, we are only processing the first MAXJOBS solution times
    MAXJOBS = 4
    solution_times = list(tp.data.load_tecplot(datafile).solution_times)[:MAXJOBS]

    # Set up the pool with initializing function and associated arguments
    num_workers = min(multiprocessing.cpu_count(), len(solution_times))
    pool = multiprocessing.Pool(num_workers, initializer=init, initargs=(datafile, stylesheet))

    try:
        # Map the work function to each of the job arguments
        pool.map(work, solution_times)
    finally:
        # !!! IMPORTANT !!!
        # Must join the process pool before parent script exits
        # to ensure Tecplot cleans up all temporary files
        # and does not create a core dump
        pool.close()
        pool.join()

import multiprocessing
import atexit
import tecplot as tp


def initialize_process(layout_file):
    # !!! IMPORTANT !!!
    # Must register stop at exit to ensure Tecplot cleans
    # up all temporary files and does not create a core dump
    atexit.register(tp.session.stop)
    
    # Set the Load-On-Demand strategy to minimize memory use to keep the RAM low
    tp.macro.execute_command("$!FileConfig LoadOnDemand { UNLOADSTRATEGY = MinimizeMemoryUse }")
    
    tp.load_layout(layout_file)
    
    
def save_image(args):
    solution_time, width, supersample, image_file = args
    
    tp.active_frame().plot().solution_time = solution_time
    tp.export.save_png(image_file, width=width, supersample=supersample)
    return image_file

    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Process layout in parallel to create images.")
    parser.add_argument("layoutfile", help="Tecplot layout file to open")
    parser.add_argument("-numprocs", help="Number of concurrent processes to run", 
        type=int, default=int(multiprocessing.cpu_count()/2), )
    parser.add_argument("-imagewidth", help="Width in pixels of the image",
        type=int, default=1024)
    parser.add_argument("-supersample", help="Supersample factor to use for image export",
        type=int, default=2)
    parser.add_argument("-imagebasename", help="Basename for exported PNG images",
        default="image")
    
    args = parser.parse_args()
    
    # Get the solution times over which to iterate. Stop PyTecplot in
    # the main process to free up the license for the workers. PyTecplot
    # cannot be restarted once stopped!
    tp.new_layout()
    tp.load_layout(args.layoutfile)
    solution_times = tp.active_frame().dataset.solution_times
    tp.session.stop()
    
    # !!! IMPORTANT !!!
    # On Linux systems, Python's multiprocessing start method
    # defaults to "fork" which is incompatible with PyTecplot
    # and must be set to "spawn"
    multiprocessing.set_start_method('spawn')
    
    # Set up the pool with initializing function and associated arguments
    pool = multiprocessing.Pool(processes=args.numprocs,
                   initializer=initialize_process,
                   initargs=(args.layoutfile,))
                   
    try:
        job_args = []
        for i,solution_time in enumerate(solution_times):
            image_file = args.imagebasename + "%04d.png"%(i)
            job_args.append((solution_time, args.imagewidth, args.supersample, image_file))
        
        image_files = pool.map(save_image, job_args)
    finally:
        # !!! IMPORTANT !!!
        # Must join the process pool before parent script exits
        # to ensure PyTecplot cleans up all temporary files
        # and does not create a core dump
        pool.close()
        pool.join()

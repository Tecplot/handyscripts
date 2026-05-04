import argparse, os

import tecplot as tp
from tecplot.constant import *

def parse_args():
    """
    This script is to be run from the command line and accepts the
    following command line arguments. Run this script with "--help"
    to see usage and help information.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--connect', action='store_true',
                        help='connect to TecUtil Server')
    parser.add_argument('-p', '--port', type=int, default=7600,
                        help='port to use when connecting to TecUtil Server')
    parser.add_argument('-n', '--nframes', type=int, default=360,
                        help='number of frames to produce in video')
    parser.add_argument('outfile', nargs='?', default='aileron_roll.mp4',
                        help='output file name')
    return parser.parse_args()

def setup_plot():
    """
    Load the F-18 dataset from Tecplot 360's examples and show the
    jet surface in 3D.
    """
    tp.new_layout()
    exdir = tp.session.tecplot_examples_directory()
    datafile = os.path.join(exdir, 'SimpleData', 'F18.plt')
    ds = tp.data.load_tecplot(datafile)

    frame = tp.active_frame()
    frame.show_border = False
    plot = frame.plot(PlotType.Cartesian3D)
    plot.activate()

    plot.contour(0).variable = ds.variable('S')
    plot.show_contour = True
    return plot

def translate_view(view, x=0, y=0, z=0):
    """
    Translate the viewer with respect to the data.
    """
    p = view.position
    view.position = p.x + x, p.y + y, p.z + z

def create_animation(outfile, plot, nframes):
    """
    Using the tp.export.animation_mpeg4() context manager, the F-18 is
    recorded doing an "aileron roll" by rotating and translating the
    viewer with respect to the data by a small amount and capturing
    each frame of the animation with a call to ani.export_animation_frame()
    """
    with tp.session.suspend():
        opts = dict(
            width=400,
            animation_speed=30,
            supersample=3,
        )
        view = plot.view
        translate_view(view, -15)
        #{DOC:highlight}[
        with tp.export.animation_mpeg4(outfile, **opts) as ani:
        #]
          for i in range(args.nframes):
            view.rotate_axes(5, (1, 0, 0))
            translate_view(view, 30 / args.nframes)
            #{DOC:highlight}[
            ani.export_animation_frame()
            #]

"""
This script is meant to run on the command line. Run with "--help" to see
usage and help information about the options it understands. It loads
the F-18 dataset from Tecplot 360's examples directory and produces a
video of the model doing an "aileron roll" by manipulating the viewer
position.
"""
args = parse_args()
if args.connect:
    tp.session.connect(port=args.port)
plot = setup_plot()
create_animation(args.outfile, plot, args.nframes)
print('video file created:', args.outfile)

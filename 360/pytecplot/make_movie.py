"""Create an MPEG-4 movie file from a sequence of images

usage:
General:
    > python make_movie.py [args]

usage examples:
Windows:
    > python .\make_movie.py -imagebasename IMAGE_ -pattern %06d -moviefilename movie.mp4

MacOS:
    > "/Applications/Tecplot 360 EX 2021 R1/bin/tec360-env" -- python3 make_movie.py -imagebasename IMAGE_ -pattern %06d -moviefilename movie.mp4

Necessary modules
-----------------
subprocess
    A module allows you to spawn new processes
glob
    A module that can capture patterns and supports recursive wildcards
argparse
    A module to write user-friendly command-line interfaces
Image
    A module for different image functions. Install using pip install Pillow

Description
-----------
This script is especially useful with the Tecplot ability to export a sequence of images.
This script will take a collection of images with a sequential number pattern and transform
it into an MPEG-4 movie file.

"""
import subprocess
import glob
import argparse
from PIL import Image

parser = argparse.ArgumentParser(description="Create an MPEG4 movie from a sequence of images.")
parser.add_argument("-imagebasename", help="Basename of input PNG images",
                    default="image")
parser.add_argument("-pattern", help="ffmpeg number pattern (e.g. %%04d)",
                    default="%04d")
parser.add_argument("-framerate", help="Framerate in frames per second",
                    type=int, default="10")
parser.add_argument("-moviefilename", help="Output movie file name. Must end in .mp4",
                    default="movie.mp4")
args = parser.parse_args()
images = glob.glob("{}*.png".format(args.imagebasename))
im = Image.open(images[0])
width, height = im.size
filepattern = "{}{}.png".format(args.imagebasename, args.pattern)

# dimensions must be even values
dimension = "{}x{}".format(int(width/2)*2, int(height/2)*2)
args = ["ffmpeg",
        "-framerate", str(args.framerate),
        "-i", filepattern,
        "-s:v", dimension,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        args.moviefilename]

# quick error handling for ffmpeg in the PATH
try:
    subprocess.run(args)
except FileNotFoundError as e:
    print(e)
    print("make_movie: This error is likely due to ffmpeg not being in your PATH.")
    print("make_movie: Please add the Tecplot bin directory to your PATH to use ffmpeg.")
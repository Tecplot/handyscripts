import subprocess
import glob
from PIL import Image

import argparse
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
print(filepattern)
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
print(args)
subprocess.run(args)

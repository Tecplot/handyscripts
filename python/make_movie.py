import subprocess
import glob
from PIL import Image

images = glob.glob("*.png")
im = Image.open(images[0])
width, height = im.size

framerate = 10
filepattern = "image%04d.png"
# dimensions must be even values
dimension = "{}x{}".format(int(width/2)*2, int(height/2)*2)
outfile = "movie.mp4"
args = ["ffmpeg", 
        "-framerate", str(framerate),
        "-i", filepattern,
        "-s:v", dimension,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        outfile]
print(args)
subprocess.run(args)

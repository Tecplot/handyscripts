from PIL import Image
import tecplot as tp
from tecplot.constant import *
import numpy as np
import os
import time
import sys

now = time.time()


def get_world_file(source_image):
    file_name, extension = os.path.splitext(source_image)
    # First try, just append a "w"
    world_file = source_image.replace(extension, extension + "w")
    if os.path.exists(world_file):
        return world_file

    # Second try, remove the second character and add the "w"
    new_ext = extension[:2] + extension[3:] + "w"
    world_file = source_image.replace(extension, new_ext)
    if os.path.exists(world_file):
        return world_file
    return None


def get_world_file_dimensions(world_file, width, height):
    world_coefficients = []
    with open(world_file, "r") as f:
        for line in f.readlines():
            world_coefficients.append(float(line))

    grid_height = height * abs(world_coefficients[3])
    left = world_coefficients[4]
    bottom = world_coefficients[5] - grid_height
    grid_width = width * world_coefficients[0]

    # left, bottom, right, top
    return [left, bottom, left + grid_width, bottom + grid_height]


def create_grid(source_image, width, height):
    tp.new_layout()
    ds = tp.active_frame().create_dataset("Image", ['x', 'y'])
    zone = ds.add_ordered_zone("ImageZone", (width + 1, height + 1))

    # left, bottom, right, top
    grid_dimensions = [0, 0, width, height]

    world_file = get_world_file(source_image)
    if world_file is not None:
        grid_dimensions = get_world_file_dimensions(world_file, width, height)

    x = np.linspace(grid_dimensions[0], grid_dimensions[2], width + 1)
    y = np.linspace(grid_dimensions[1], grid_dimensions[3], height + 1)
    yy, xx = np.meshgrid(y, x, indexing='ij')
    zone.values('x')[:] = xx.ravel()
    zone.values('y')[:] = yy.ravel()

    tp.data.operate.execute_equation("{r} = 0", value_location=ValueLocation.CellCentered)
    tp.data.operate.execute_equation("{g} = 0", value_location=ValueLocation.CellCentered)
    tp.data.operate.execute_equation("{b} = 0", value_location=ValueLocation.CellCentered)
    return zone

# Image returns pixel values from top down (XMin,YMax) to (XMax,YMin)
# +---+---+
# | 0 | 2 |
# +---+---+
# | 1 | 3 |
# +---+---+
#
# For cell centered values, Tecplot has "ghost cells" which need to be ignored.  Tecplot's cell numbering would look like this:
#
# +---+---+
# | 3 | 4 | 5
# +---+---+
# | 0 | 1 | 2
# +---+---+
#
# Where the values hanging off the side are ghost cells.
#


def main(infile, outfile):
    source_image = infile
    dest_file = outfile

    im = Image.open(source_image)
    pix = im.load()
    width, height = im.size

    zone = create_grid(source_image, width, height)

    cell_count = len(zone.values('r').as_numpy_array())
    r = np.zeros(cell_count)
    g = np.zeros(cell_count)
    b = np.zeros(cell_count)

    imax = width
    jmax = height

    pixels = list()
    for j in range(jmax - 1, -1, -1):
        for i in range(imax):
            pixels.append(pix[i, j])

    index = 0
    for j in range(jmax):
        for i in range(imax + 1):
            if i == imax:
                pass
            else:
                tp_index = i + j * (imax + 1)
                r[tp_index] = pixels[index][0]
                g[tp_index] = pixels[index][1]
                b[tp_index] = pixels[index][2]
                index += 1

    zone.values('r')[:] = r
    zone.values('g')[:] = g
    zone.values('b')[:] = b

    tp.data.save_tecplot_plt(dest_file)
    print(time.time() - now)


if len(sys.argv) != 3:
    print("Usage: ImagetoPLT.py <image file name> <plt file name>")
else:
    infile = sys.argv[1]
    outfile = sys.argv[2]
    main(infile, outfile)

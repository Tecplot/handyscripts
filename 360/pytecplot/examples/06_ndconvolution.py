from os import path
from scipy.ndimage.filters import convolve
import tecplot as tp

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tp.session.connect()

# 3D volume data
# This is for illustration of the mathematical process only
# and a convolution of RHO and E is probably meaningless here.
examples_dir = tp.session.tecplot_examples_directory()
ds = tp.data.load_tecplot(path.join(examples_dir, 'SimpleData', 'DownDraft.plt'))

# The data looks like this
# >>> print(ds)
# Dataset:
#  Zones: ['G1']
#  Variables: ['X','Y','Z','RHO','RHO-U','RHO-V','RHO-W','E']

# Pull in the data from Tecplot into numpy arrays
g1 = ds.zone('G1')
g1_rho = g1.values('RHO')
g1_e = g1.values('E')
rho = g1_rho.as_numpy_array()
rho.shape = g1_rho.shape
e = g1_e.as_numpy_array()
e.shape = g1_e.shape

# Do the convolution. Filter RHO with weights from E.
# see scipy documentation for details.
# https://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.ndimage.filters.convolve.html
result = convolve(rho, e, mode='constant', cval=0)

# We have the result as a numpy array and we want to
# push it into a new variable in the Tecplot dataset
conv_var = ds.add_variable('conv')
conv = conv_var.values('G1')
conv[:] = result.ravel()

# Verify the data is there.
# should print:
#   [ 62688124.  73131632.  83576288. ...,  71433192.  62505044.  53579468.]
print(ds.zone('G1').values('conv').as_numpy_array())

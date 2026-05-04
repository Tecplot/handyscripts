import os
import tecplot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'F18.lay')

# Load a stylized layout where the contour variable is set to 'Nj'
tecplot.load_layout(infile)
current_dataset = tecplot.active_frame().dataset

# export original image
tecplot.export.save_png('F18_orig.png', 600, supersample=3)

# alter variable 'Nj' for the the two wing zones in the dataset
# In this simple example, just multiply it by 10.
tecplot.data.operate.execute_equation('{Nj}={Nj}*10',
    zones=[current_dataset.zone('right wing'),
           current_dataset.zone('left wing')])

# The contour color of the wings in the exported image will now be
# red, since we have altered the 'Nj' variable by multiplying it by 10.
tecplot.export.save_png('F18_altered.png', 600, supersample=3)

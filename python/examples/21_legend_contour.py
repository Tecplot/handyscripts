import os

import numpy as np

import tecplot
from tecplot.constant import *

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

# By loading a layout many style and view properties are set up already
examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'SimpleData', 'RainierElevation.lay')
tecplot.load_layout(datafile)

frame = tecplot.active_frame()
plot = frame.plot()

# Rename the elevation variable
frame.dataset.variable('E').name = "Elevation (m)"

# Set the levels to nice values
plot.contour(0).levels.reset_levels(np.linspace(200,4400,22))

legend = plot.contour(0).legend
legend.show = True
legend.vertical = False  # Horizontal
legend.auto_resize = False
legend.label_step = 5

legend.overlay_bar_grid = False
legend.position = (55, 94)  # Frame percentages

legend.box.box_type = TextBox.None_ # Remove Text box

legend.header_font.typeface = 'Courier'
legend.header_font.bold = True

legend.number_font.typeface = 'Courier'
legend.number_font.bold = True

tecplot.export.save_png('legend_contour.png', 600, supersample=3)

import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import tecplot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.lay')

tecplot.load_layout(infile)
tecplot.export.save_png('layout_example.png', 600, supersample=3)

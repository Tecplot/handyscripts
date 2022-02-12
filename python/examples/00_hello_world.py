import logging
logging.basicConfig(level=logging.DEBUG)

import tecplot

# Run this script with "-c" to connect to Tecplot 360 on port 7600
# To enable connections in Tecplot 360, click on:
#   "Scripting" -> "PyTecplot Connections..." -> "Accept connections"
import sys
if '-c' in sys.argv:
    tecplot.session.connect()

tecplot.new_layout()

frame = tecplot.active_frame()
frame.add_text('Hello, World!', position=(36, 50), size=34)
tecplot.export.save_png('hello_world.png', 600, supersample=3)

import sys
import logging

import tecplot

log = logging.getLogger()
log.setLevel(logging.DEBUG)

frame = tecplot.active_frame()
frame.add_text('Hello, World!', position=(35,50), size=35)
tecplot.export.save_png('hello_world.png')

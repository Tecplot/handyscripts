from os import path
import numpy as np
import tecplot as tp

# load layout
examples_dir = tp.session.tecplot_examples_directory()
example_layout = path.join(examples_dir,'SimpleData','3ElementWing.lpk')
tp.load_layout(example_layout)
frame = tp.active_frame()

#{DOC:highlight}[
levels = frame.plot().contour(0).levels
levels.reset_levels(np.linspace(55000,115000,61))
#]

# save image to file
tp.export.save_png('contour_adjusted_levels.png', 600, supersample=3)

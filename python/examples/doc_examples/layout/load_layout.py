import os
import tecplot as tp

frame = tp.active_frame()

examples = tp.session.tecplot_examples_directory()
layoutfile = os.path.join(examples, 'SimpleData', 'F18.lay')
#{DOC:highlight}[
tp.load_layout(layoutfile)
#]

# frame object is no longer usable.
# the following will print:
#       <class 'ValueError'> 255 is not a valid PlotType
try:
    frame.plot_type
except Exception as e:
    print(type(e),e)

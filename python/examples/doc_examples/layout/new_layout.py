import tecplot

frame = tecplot.active_frame()
#{DOC:highlight}[
tecplot.new_layout()
#]

# frame object is no longer usable.
# the following will print:
#       <class 'ValueError'> 255 is not a valid PlotType
try:
    frame.plot_type
except Exception as e:
    print(type(e),e)

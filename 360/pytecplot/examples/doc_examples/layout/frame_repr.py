import tecplot
from tecplot.layout import Frame, Page

frame = tecplot.active_frame()

'''
The "repr" string of the Frame is executable code.
The following will print: "Frame(uid=11, page=Page(uid=1))"
'''
print(repr(frame))

frame2 = None
exec('frame2 = '+repr(frame))

'''
At this point, frame2 is just another handle to
the exact same frame object in the Tecplot Engine
'''
assert frame2 == frame

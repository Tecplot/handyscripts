import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()

line0 = frame.add_polyline([[30,30], [50,60]], coord_sys=CoordSys.Frame)
line1 = frame.add_polyline([[35,30], [55,60]], coord_sys=CoordSys.Frame)
line2 = frame.add_polyline([[40,30], [60,60]], coord_sys=CoordSys.Frame)

#{DOC:highlight}[
line0.arrowhead.attachment = ArrowheadAttachment.AtEnd
line1.arrowhead.attachment = ArrowheadAttachment.AtEnd
line2.arrowhead.attachment = ArrowheadAttachment.AtEnd
#]

line0.line_thickness = 2
line1.line_thickness = 2
line2.line_thickness = 2

tp.export.save_png('arrowhead.png', 600)

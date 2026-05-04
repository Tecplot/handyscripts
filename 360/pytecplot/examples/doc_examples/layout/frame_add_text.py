import tecplot
from tecplot.constant import Color

frame = tecplot.active_frame()
#{DOC:highlight}[
frame.add_text('Hello, World!', position=(35, 50),
               bold=True, italic=False, color=Color.Blue)
#]

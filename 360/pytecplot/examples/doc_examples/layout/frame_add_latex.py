import tecplot as tp
from tecplot.constant import TextAnchor

frame = tp.active_frame()
#{DOC:highlight}[
frame.add_latex(r'$$\zeta(s) = \sum_{n=1}^\infty\frac{1}{n^s}$$',
                (50,50), size=64, anchor=TextAnchor.Center)
#]

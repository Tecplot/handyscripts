import tecplot as tp
from tecplot.constant import *

frame = tp.active_frame()
frame.add_latex(r'''$
    \rho\frac{D\vec{u}}{Dt} =
        -\vec{\nabla}p + \vec{\nabla}\cdot\vec{\tau} + \rho\vec{g}
    $''', (50,50), size=32, anchor=TextAnchor.Center)

tp.export.save_png('latex_annotation.png')

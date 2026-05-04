from os import path
import numpy as np

import tecplot as tp
from tecplot.constant import PlotType

examples = tp.session.tecplot_examples_directory()
datafile = path.join(examples, 'SimpleData', 'F18.plt')
ds = tp.data.load_tecplot(datafile)
fr = tp.active_frame()
fr.plot_type = PlotType.Cartesian3D

# probe a single point
#{DOC:highlight}[
res = tp.data.query.probe_on_surface((13.5, 4.0, 0.6 ))
#]

'''
The following line will print:
    (13.499723788684996, 3.9922783797612795, 0.49241572276992346,
    0.0018958827755862578, 0.07313805429221854, 0.997276718375976,
    0.06335166319722907)
'''
print(res.data)

# probe multiple points
points = np.array([[13.5,  4.0, 0.6],  # just above starboard wing
                   [13.5, -4.0, 0.6]]) # just above port wing

#{DOC:highlight}[
res = tp.data.query.probe_on_surface(points.transpose())
#]
values = np.array(res.data).reshape((-1, len(points))).transpose()

'''
The following will print the probed position and the result of the probe
    [ 13.5   4.    0.6] [  1.34997238e+01   3.99227838e+00   4.92415723e-01
       1.89588278e-03   7.31380543e-02   9.97276718e-01   6.33516632e-02]
    [ 13.5  -4.    0.6] [  1.34997238e+01  -3.99227838e+00   4.92415723e-01
       1.89588278e-03   7.31380543e-02   9.97276718e-01   6.33516632e-02]
'''
for pt, v in zip(points, values):
    print(pt, v)

import os
import tecplot
from tecplot.constant import PlotType

frame = tecplot.active_frame()
assert frame.plot_type is PlotType.Sketch

install_dir = tecplot.session.tecplot_install_directory()
infile = os.path.join(install_dir, 'examples', 'SimpleData', 'SpaceShip.lpk')
tecplot.load_layout(infile)

frame = tecplot.active_frame()
assert frame.plot_type is PlotType.Cartesian3D

frame.plot_type = PlotType.Cartesian2D
assert frame.plot_type is PlotType.Cartesian2D

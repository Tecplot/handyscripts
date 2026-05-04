import os
import tecplot
from tecplot.constant import PlotType

install_dir = tecplot.session.tecplot_install_directory()
infile = os.path.join(install_dir, 'examples', 'SimpleData', 'SpaceShip.lpk')
tecplot.load_layout(infile)

frame = tecplot.active_frame()
assert frame.plot_type is PlotType.Cartesian3D

plot3d = frame.plot()
plot3d.show_contour = True

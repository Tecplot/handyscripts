import os
import tecplot

#{DOC:highlight}[
install_dir = tecplot.session.tecplot_install_directory()
#]
infile = os.path.join(install_dir, 'examples', 'SimpleData', 'SpaceShip.lpk')

tecplot.load_layout(infile)
tecplot.export.save_png('spaceship.png', 600, supersample=3)

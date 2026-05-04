from os import path
import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, MeshType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
dataset = tp.data.load_tecplot(infile)

# Enable 3D field plot and turn on contouring
frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian3D
plot = frame.plot()
plot.show_mesh = True

contour = plot.contour(0)
contour.variable = dataset.variable('S')
contour.colormap_name = 'Doppler'
contour.levels.reset_levels(np.linspace(0.02,0.12,11))

# set the mesh type and color for all zones
#{DOC:highlight}[
mesh = plot.fieldmaps().mesh
mesh.mesh_type = MeshType.HiddenLine
mesh.color = contour
#]

# save image to file
tp.export.save_png('fieldmap_mesh.png', 600, supersample=3)

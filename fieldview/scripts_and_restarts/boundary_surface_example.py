import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

fv.view.reset()

bnd = fv.vis.create_boundary(ds, types=fv.constant.BoundaryTypeSelection.ALL)
bnd.coloring = fv.constant.Coloring.SCALAR
bnd.scalar_func = ds.scalar_functions[0]
bnd.display_type = fv.constant.DisplayType.MESH
bnd.colormap.name = fv.constant.ColormapName.SPECTRUM

fv.camera.zoom(16.0)
fv.camera.pan(0.06, -0.065)

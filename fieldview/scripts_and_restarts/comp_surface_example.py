import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

cs = fv.vis.create_comp(ds, grid=1, plane=fv.constant.Plane.I)
cs.i_plane.value = 10
cs.coloring = fv.constant.Coloring.SCALAR
cs.colormap.name = fv.constant.ColormapName.SPECTRUM

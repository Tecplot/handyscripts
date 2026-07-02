import os

import fieldview as fv


# Prep script: load data and create one boundary surface in the scene.
data_dir = os.path.join(fv.home, "examples", "f18")
ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

bnd = fv.vis.create_boundary(ds, types=fv.constant.BoundaryTypeSelection.ALL)


print("Prepared with one boundary surface.")

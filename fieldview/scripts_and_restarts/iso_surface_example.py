import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

fv.view.reset()

bnd = fv.vis.create_boundary(
    ds,
    types=fv.constant.BoundaryTypeSelection.ALL,
    display_type=fv.constant.DisplayType.SMOOTH,
)

iso_func_name = "Mach number [PLOT3D]"
iso = fv.vis.create_iso(ds, iso_func=iso_func_name)
iso.iso_value.value = 0.31
iso.coloring = fv.constant.Coloring.SCALAR
iso.display_type = fv.constant.DisplayType.SMOOTH
iso.transparency = 0.5

fv.camera.zoom(4.0)
fv.camera.pan(0.0, -0.05)

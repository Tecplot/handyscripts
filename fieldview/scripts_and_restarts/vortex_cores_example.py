import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

vc = fv.vis.create_vortex_cores(
    ds,
    method=fv.constant.VortexCoreMethod.VORTICITY_ALIGNMENT,
    vector_func=ds.vector_functions[0],
)
vc.coloring = fv.constant.Coloring.SCALAR
vc.scalar_path_variable = "Vortex Strength"
vc.colormap.name = fv.constant.ColormapName.SPECTRUM

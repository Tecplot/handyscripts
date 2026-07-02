import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

x_min = ds.xmin
x_max = ds.xmax
step = (x_max - x_min) / 19.0 if x_max != x_min else 0.0

fv.view.set_outline(False)

for i in range(20):
    cs = fv.vis.create_coord(
        ds,
        plane=fv.constant.Plane.X,
        x_plane=fv.RangedValue(value=x_min + i * step),
        transparency=0.75,
    )
    cs.coloring = fv.constant.Coloring.SCALAR
    cs.scalar_func = ds.scalar_functions[0]
    cs.display_type = fv.constant.DisplayType.CONSTANT

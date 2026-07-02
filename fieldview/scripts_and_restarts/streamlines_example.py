import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

fv.view.set_outline(True)
fv.view.reset()

bnd = fv.vis.create_boundary(
    ds,
    types=fv.constant.BoundaryTypeSelection.ALL,
    display_type=fv.constant.DisplayType.SMOOTH,
)

sl = fv.vis.create_streamlines(
    ds,
    vector_func="Velocity Vectors [PLOT3D]",
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=ds.scalar_functions[0],
    display_type=fv.constant.PathsDisplayType.RIBBONS,
    seed_coord=fv.constant.StreamlinesSeedCoord.XYZ,
    ribbon_width=4,
)

start = (0.25, 0.0, 0.25)
end = (1.5, 0.0, 0.25)
num_seeds = 10

seeds = [
    (
        start[0] + (end[0] - start[0]) * i / (num_seeds - 1),
        start[1] + (end[1] - start[1]) * i / (num_seeds - 1),
        start[2] + (end[2] - start[2]) * i / (num_seeds - 1),
    )
    for i in range(num_seeds)
]

sl.add_seeds(seeds)
sl.calculate()

fv.camera.zoom(6.0)
fv.camera.pan(0.0, -0.075)

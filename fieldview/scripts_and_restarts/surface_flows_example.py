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

sf = fv.vis.create_surface_flows(
    ds,
    mode=fv.constant.SurfaceFlowMode.EULER,
    vector_func="Velocity Vectors [PLOT3D]",
    coloring=fv.constant.Coloring.SCALAR,
    scalar_path_variable=ds.scalar_functions[0],
    direction=fv.constant.CalculationDirection.BOTH,
    seeding=fv.constant.SurfaceFlowSeeding.MEDIUM_DENSITY,
    step=21,
)
sf.scalar_path_variable = "Speed of sound [PLOT3D]"
sf.calculate()

sf.colormap.use_local = True

fv.camera.zoom(16.0)
fv.camera.pan(0.06, -0.065)

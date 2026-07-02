import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds1 = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

ds2 = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
    input_mode=fv.constant.InputMode.APPEND,
)

qcrit = fv.formula.create(
    "Qcrit",
    'Qcriterion("Velocity Vectors [PLOT3D]")',
)

vel_mag = fv.formula.create(
    "Velocity Magnitude",
    fv.formula.mag("Velocity Vectors [PLOT3D]"),
)

delta_p = fv.formula.create(
    "Delta Pressure",
    fv.formula.dataset_quantity(2, "Pressure [PLOT3D]")
    - fv.formula.dataset_quantity(1, "Pressure [PLOT3D]"),
)

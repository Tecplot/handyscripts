import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

# First load (replace).
ds0 = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

# Second load (append) using local-parallel.
ds1 = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
    input_mode=fv.constant.InputMode.APPEND,
    server_config=fv.constant.ServerConfig.LOCAL_PARALLEL,
)

# Mirror and translate the appended dataset (apply immediately).
ds1.duplication.mirror.axes = fv.constant.Axes.Z
ds1.transform.translate = (0.0, 0.0, 15.0)

print("Grids:", ds0.num_grids, ds1.num_grids)

fv.view.reset()
fv.camera.zoom(2.0)

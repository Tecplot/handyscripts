import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

display_probe = fv.data.probe((0.01, 0.02, 0.01), dataset=ds)
ijk_probe = fv.data.probe_ijk((2, 3, 4), grid=1, dataset=ds)

print("Display probe scalar:", display_probe.scalar)
print("IJK probe point:", ijk_probe.point)

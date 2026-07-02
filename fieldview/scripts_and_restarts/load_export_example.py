import os

import fieldview as fv


# Resolve the bundled example dataset under the FieldView install root.
data_dir = os.path.join(fv.home, "examples", "f18")

# Load Plot3D (grid + results).
ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

# Simple query and export.
print("Grids:", ds.num_grids)
output_png = os.path.join(os.path.expanduser("~"), "fv_plot3d.png")
fv.export_png(output_png)
print(f"Saved image: {output_png}")

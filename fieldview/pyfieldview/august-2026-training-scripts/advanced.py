from pathlib import Path

import fieldview as fv
import numpy as np

# Load the transient FVUNS dataset.
example_dir = Path(fv.home) / "examples" / "rectangular_duct"
uns_file = example_dir / "rect_duct_001.uns"

ds = fv.data.load_fvuns(uns_file, transient=True)

# Create a coordinate surface in the middle of the dataset.
z_mid = (ds.zmin + ds.zmax) / 2
temp_var = "temperature"
cs = fv.vis.create_coord(
    ds,
    plane=fv.constant.Plane.Z,
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=temp_var,
    display_type=fv.constant.DisplayType.CONSTANT,
)
cs.z_plane.value = z_mid

# Use Viridis for temperature coloring.
cs.colormap.name = fv.constant.ColormapName.VIRIDIS

# Average temperature over all transient time steps and load it as a new scalar.
info = ds.transient_info()
step_values = info.time_step_values
step_count = info.total_time_steps
sum_by_grid: dict[int, np.ndarray] = {}
orig_step = info.time_step

for i, step in enumerate(step_values, start=1):
    ds.set_transient(time_step=step)
    for grid in range(1, ds.num_grids + 1):
        arr = np.asarray(ds.scalars.to_numpy(temp_var, grid=grid, copy=True), dtype=np.float64)
        if grid in sum_by_grid:
            sum_by_grid[grid] += arr
        else:
            sum_by_grid[grid] = arr

avg_var = "temperature average"
ds.set_transient(time_step=orig_step)
for grid, total in sum_by_grid.items():
    avg_arr = total / step_count
    ref = ds.scalars.create(avg_var , avg_arr, grid=grid)

cs.scalar_func = avg_var

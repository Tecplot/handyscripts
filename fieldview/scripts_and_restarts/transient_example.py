import os

import fieldview as fv


uns_file = os.path.join(fv.home, "examples", "rectangular_duct", "rect_duct_010.uns")

# Load the dataset in transient mode.
ds = fv.data.load_fvuns(uns_file, transient=True)

# Query the available time-step and solution-time values.
info = ds.transient_info()
print("Current step:", info.time_step)
print("First three steps:", info.time_step_values[:3])

# Select a specific time step for inspection.
ds.set_transient(time_step=25)

cs = fv.vis.create_coord(
    ds,
    plane=fv.constant.Plane.Z,
    coloring=fv.constant.Coloring.SCALAR,
    display_type=fv.constant.DisplayType.CONSTANT,
)

# Sweep all transient time steps (default: step indices 0 to -1).
ds.sweep_time()

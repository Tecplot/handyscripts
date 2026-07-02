import os

import fieldview as fv

# Load sample PLOT3D dataset bundled with FieldView.
data_dir = os.path.join(fv.home, "examples", "f18")
ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)
# Add a boundary surface so camera motion is visible.
fv.vis.create_boundary(
    ds,
    types=fv.constant.BoundaryTypeSelection.ALL,
    display_type=fv.constant.DisplayType.SMOOTH,
)

print(f"Loaded dataset_id={ds.dataset_id}")

fv.view.reset()
fv.view.set_perspective(True, angle=25.0)

# Capture deterministic state before scripted camera motion.
# Use get_state()/set_state() for exact replay across sessions.
baseline_state = fv.camera.get_state()
print("Deterministic view state:", baseline_state)

# Set a reproducible starting camera pose.
fv.camera.look_at(
    eye=(-1.0, 0.0, 0.0),
    target=(0.0, 0.0, 0.0),
    up=(0.0, 1.0, 0.0),
)

# Inspect pose after look_at().
# Use get_pose() for pose-style workflows (eye/target/up).
pose = fv.camera.get_pose()
print("Pose after look_at:", pose)

# Run the orbit sequence.
for _ in range(90):
    fv.camera.orbit(1.0, 0.0)

for _ in range(90):
    fv.camera.orbit(-1.0, 0.0)

for _ in range(90):
    fv.camera.orbit(0.0, 1.0)

for _ in range(90):
    fv.camera.orbit(0.0, -1.0)

# Log final pose and deterministic state after scripted motion.
print("Final pose:", fv.camera.get_pose())
print("Final deterministic view state:", fv.camera.get_state())

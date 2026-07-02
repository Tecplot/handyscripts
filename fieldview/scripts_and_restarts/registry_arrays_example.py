import os

import numpy as np

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")
ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

scalar_name = ds.scalar_functions[0]
vector_name = ds.vector_functions[0]
distance_field_name = "Distance From Point"
vector_to_point_field_name = "Vector To Point"

# Show array-view behavior on the first grid.
pressure = ds.scalars.to_numpy(scalar_name, grid=1, copy=False)
velocity = ds.vectors.to_numpy(vector_name, grid=1, copy=False)
xyz = ds.positions.to_numpy(grid=1, copy=False)

# copy=False returns read-only NumPy views when possible.
# The returned arrays keep the snapshot backing alive, so they remain valid
# even after the local ``snap`` variable is gone.
print("pressure writeable:", pressure.flags.writeable)
print("velocity shape:", velocity.shape)
print("xyz shape:", xyz.shape)

ref_point = np.array([2.0, 1.0, 0.05], dtype=float)

# Create/update registry arrays on every dataset grid.
for grid in range(1, ds.num_grids + 1):
    xyz_grid = ds.positions.to_numpy(grid=grid, copy=False)
    vector_to_point = ref_point - np.array(xyz_grid, copy=True)
    distance = np.linalg.norm(vector_to_point, axis=1)

    ds.scalars.create(distance_field_name, distance, grid=grid)
    ds.vectors.create(vector_to_point_field_name, vector_to_point, grid=grid)

# Create a Z-plane coordinate surface and color it by the distance field.
coord = fv.vis.create_coord(
    ds,
    plane=fv.constant.Plane.Z,
    z_plane=fv.RangedValue(value=0.05),
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=distance_field_name,
    vector_func=vector_to_point_field_name,
    display_type=fv.constant.DisplayType.CONSTANT,
)

# Create a second Z-plane coord surface with vector display.
coord_vectors = fv.vis.create_coord(
    ds,
    plane=fv.constant.Plane.Z,
    z_plane=fv.RangedValue(value=0.05),
    coloring=fv.constant.Coloring.GEOMETRIC,
    geometric_color=fv.constant.GeometricColor.WHITE,
    vector_func=vector_to_point_field_name,
    display_type=fv.constant.DisplayType.VECTORS,
    vector_options=fv.VectorOptions(vector_scale=2.0),
)

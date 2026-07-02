import os
from typing import Optional

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

fv.view.reset()

scalar_name = ds.scalar_functions[0]
probe = fv.data.probe_ijk((2, 3, 4), grid=1, dataset=ds)

boundary = fv.vis.create_boundary(ds, types=fv.constant.BoundaryTypeSelection.ALL)
boundary.scalar_func = scalar_name

coord = fv.vis.create_coord(ds)
coord.scalar_func = scalar_name
coord.plane = fv.constant.Plane.X
coord.x_plane.value = probe.point.x

boundary_result = boundary.integrate()
coord_partial_result = coord.integrate_partial_surface(tuple(probe.point))

print(boundary_result)
print(coord_partial_result)


def _integration_summary(
    label: str, result: Optional[fv.data.IntegrationResult]
) -> str:
    if result is None:
        return f"{label}: no result"
    average = "n/a" if result.average is None else f"{result.average:.6g}"
    return f"{label}: sum={result.sum:.6g}, area={result.area:.6g}, avg={average}"


fv.vis.create_annotation_text(
    "\n".join(
        [
            _integration_summary("Boundary", boundary_result),
            _integration_summary("Coord partial", coord_partial_result),
        ]
    ),
    position=(20, 80),
    color=fv.constant.GeometricColor.WHITE,
    font_size=18,
)

fv.camera.pan(0.25, -0.1)

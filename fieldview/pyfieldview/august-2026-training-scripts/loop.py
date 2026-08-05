# This script is for the 2026 PyFV Debut Webinar
#
# It assumes nothing.
#
# It does the following:
#     - Loads F18 dataset
#     - Activates all boundary surfaces
#     - Creates a cut plane (coordinate surface)
#     - Exports an image to cwd

import pathlib

import fieldview as fv
from fieldview.vis import Coord

current_dir = pathlib.Path(__file__).parent

data_dir = pathlib.Path(fv.home, "examples", "f18")
ds = fv.data.load_plot3d(
    data_dir / "f18i9b_g_bin",
    data_dir / "f18i9b_q_bin",
)

ds.duplication.mirror.axes = fv.constant.Axes.Z

fv.vis.create_boundary(
    ds,
    types=fv.constant.BoundaryTypeSelection.ALL,
    coloring=fv.constant.Coloring.SCALAR,
    display_type=fv.constant.DisplayType.SMOOTH,
    scalar_func="Pressure [PLOT3D]"
)

coord_locations = [0, 0.25, 0.5, 0.75, 1]
coords: list[Coord] = []
minx = 0
maxx = 3
for loc in coord_locations:
    coord = fv.vis.create_coord(
        ds,
        plane=fv.constant.Plane.X,
        coloring=fv.constant.Coloring.SCALAR,
        display_type=fv.constant.DisplayType.CONSTANT,
        visibility=False
    )
    coord.x_plane.value = (minx + maxx) * loc
    coords.append(coord)

fv.view.set_outline(False)
fv.view.align("+x")
fv.view.center()
fv.camera.zoom(0.5)
fv.camera.pan(-0.3, -0.3)
fv.camera.look_at((0,0,0))

text = fv.vis.create_annotation_text(
    "PLACEHOLDER", 
    position = (210, 175),
    color=fv.constant.GeometricColor.BLACK
)

for i, coord in enumerate(coords):
    text.text = f"COORD SURFACE @ X={coord.x_plane.value}"
    coord.visibility = True
    fv.export_png(current_dir / "images" / f"loop-x={coord.x_plane.value}.png")
    coord.visibility = False

# This script is for the 2026 PyFV Debut Webinar
#
# It assumes:
#     - Dataset is loaded
#     - Boundary surface is in place
#
# It does the following:
#     - Creates a coordinate surface
#     - Exports an image to cwd

import pathlib

import fieldview as fv

current_dir = pathlib.Path(__file__).parent

ds = fv.data.get_current()

# TODO: Fill in coordinate surface creation
# To get autocomplete, use pip install:
#     e.g., pip install "C:\Program Files\Tecplot\FieldView 2026 R1\pyfieldview\wheels\fieldview-1.0.0-cp313-cp313-win_amd64.whl"

coord = fv.vis.create_coord(
    ds,
    plane=fv.constant.Plane.Y,
    coloring=fv.constant.Coloring.SCALAR,
    display_type=fv.constant.DisplayType.SMOOTH,
    scalar_func="Pressure [PLOT3D]"
)

mid = (coord.y_plane.range.min + coord.y_plane.range.max) / 2

coord.y_plane.value = mid

fv.export_png(current_dir / "images" / "simple.png")

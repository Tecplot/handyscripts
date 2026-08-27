"""Export pressure and Cp contour PNGs on coordinate sections.

How to use:
1. Edit only the clearly marked CUSTOMIZE block below.
2. Enter the exact FieldView loader and scalar-function names.
3. Select X, Y, or Z and list one or more coordinate values to export.
4. Execute this file inside FieldView. Incorrect names produce errors listing
   the exact loaders or scalar functions available for selection.

Each scalar is exported at every SECTION_VALUES entry. Output filenames use
the pattern AXIS_POSITION_SCALAR.png, for example ``Z_1.57_Cp.png``.
"""

from pathlib import Path

import fieldview as fv


# =============================================================================
# CUSTOMIZE FOR YOUR DATA -- EDIT THIS BLOCK
# =============================================================================

# 1) Data loading
# Use the exact function name found under fieldview.data, including "load_".
# Example for OpenFOAM direct: "load_openfoam_direct" with system/controlDict.
# This template expects a loader with one primary input file. A loader requiring
# separate grid/results files needs corresponding arguments in the load call.
LOADER_NAME = "load_openfoam_direct"
INPUT_FILE = Path(r"***DataPath***")

# True loads transient data and selects its final solution time.
# False loads steady data and skips transient-time selection.
TRANSIENT = True

# 2) Exact scalar names
# PRESSURE_NAME and every SCALAR_EXPORTS name must match ds.scalar_functions.
PRESSURE_NAME = "p"
CP_NAME = "Cp"

# 3) Cp = (pressure - reference pressure) / (0.5 * density * velocity^2)
# If CP_NAME already exists, it is reused. For OpenFOAM kinematic pressure p/rho,
# keep REFERENCE_DENSITY = 1.0; use consistent density for dimensional pressure.
REFERENCE_PRESSURE = 0.0
REFERENCE_DENSITY = 1.0
REFERENCE_VELOCITY = 1.0

# 4) Coordinate sections
# SECTION_AXIS accepts "X", "Y", or "Z". Every listed position is exported.
SECTION_AXIS = "Z"
SECTION_VALUES = (1.57, 0.5)

# 5) Scalars and their fixed (minimum, maximum) color ranges
SCALAR_EXPORTS = (
    (PRESSURE_NAME, (-1.2, 0.6)),
    (CP_NAME, (-2.4, 1.2)),
)

# 6) Image appearance and output
CONTOUR_COUNT = 21
LEGEND_LABEL_COUNT = 5
LEGEND_POSITION = (0.68, 0.88)
CAMERA_DISTANCE_SCALE = 3.0

# This default creates an Output folder beside the Script folder.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Output"

# =============================================================================
# END CUSTOMIZATION -- THE WORKFLOW BELOW NORMALLY NEEDS NO EDITING
# =============================================================================

# Stop immediately if the visible input-path placeholder was not replaced.
if "***" in str(INPUT_FILE):
    raise ValueError("Replace INPUT_FILE in the CUSTOMIZE block")

# Resolve and validate the named loader and customization values.
if not LOADER_NAME.startswith("load_"):
    raise ValueError("LOADER_NAME must be a fieldview.data load_* function name")
data_loader = getattr(fv.data, LOADER_NAME, None)
if not callable(data_loader):
    available_loaders = sorted(
        name for name in dir(fv.data) if name.startswith("load_")
    )
    raise ValueError(
        f"fieldview.data.{LOADER_NAME} was not found. Available: {available_loaders}"
    )
if not INPUT_FILE.is_file():
    raise FileNotFoundError(f"Input data file was not found: {INPUT_FILE}")
if SECTION_AXIS.upper() not in {"X", "Y", "Z"}:
    raise ValueError("SECTION_AXIS must be X, Y, or Z")
if not SECTION_VALUES:
    raise ValueError("SECTION_VALUES must contain at least one coordinate")
if not SCALAR_EXPORTS:
    raise ValueError("SCALAR_EXPORTS must contain at least one scalar and range")
for scalar_name, color_range in SCALAR_EXPORTS:
    if len(color_range) != 2:
        raise ValueError(f"Color range for {scalar_name!r} must contain min, max")
if len(LEGEND_POSITION) != 2:
    raise ValueError("LEGEND_POSITION must contain X, Y")
if REFERENCE_DENSITY <= 0.0 or REFERENCE_VELOCITY <= 0.0:
    raise ValueError("Reference density and velocity must be greater than zero")
if CAMERA_DISTANCE_SCALE <= 0.0:
    raise ValueError("CAMERA_DISTANCE_SCALE must be greater than zero")

axis = SECTION_AXIS.upper()
ds = data_loader(str(INPUT_FILE), transient=TRANSIENT)
if TRANSIENT:
    final_time = ds.transient_info().solution_time_values[-1]
    ds.set_transient(solution_time=final_time)

# Exact-name checks prevent a similarly named scalar being selected.
if PRESSURE_NAME not in ds.scalar_functions:
    raise RuntimeError(
        f"Scalar {PRESSURE_NAME!r} was not found. Available: {ds.scalar_functions}"
    )

# Create Cp only when it is requested but does not already exist.
# Coordinate sections are defined by a plane and need no boundary name.
requested_scalars = tuple(name for name, _ in SCALAR_EXPORTS)
if CP_NAME in requested_scalars and CP_NAME not in ds.scalar_functions:
    fv.formula.create(
        CP_NAME,
        (fv.formula.quantity(PRESSURE_NAME) - REFERENCE_PRESSURE)
        / (0.5 * REFERENCE_DENSITY * REFERENCE_VELOCITY**2),
    )

missing_scalars = [name for name in requested_scalars if name not in ds.scalar_functions]
if missing_scalars:
    raise RuntimeError(
        f"Scalars {missing_scalars} were not found. Available: {ds.scalar_functions}"
    )

# Create one coordinate section using the selected axis and first position.
plane_by_axis = {
    "X": fv.constant.Plane.X,
    "Y": fv.constant.Plane.Y,
    "Z": fv.constant.Plane.Z,
}
fv.view.reset()
fv.view.set_outline(False)
section = fv.vis.create_coord(
    ds,
    plane=plane_by_axis[axis],
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=requested_scalars[0],
    display_type=fv.constant.DisplayType.SMOOTH,
    contours=fv.constant.ContourColoring.BLACK,
    show_mesh=False,
    **{f"{axis.lower()}_plane": fv.RangedValue(value=SECTION_VALUES[0])},
)
section.colormap.name = fv.constant.ColormapName.SPECTRUM
section.colormap.filled_contour = True
section.colormap.use_local = False
section.colormap.num_contours = CONTOUR_COUNT
section.legend.show = True
section.legend.spectrum.colorbar = True
section.legend.spectrum.num_labels = LEGEND_LABEL_COUNT
section.legend.relative_position = LEGEND_POSITION

# Set a normal view to the selected plane and reuse it for every image.
bounds = fv.data.get_session_state().bounds
center = [
    0.5 * (bounds.xmin + bounds.xmax),
    0.5 * (bounds.ymin + bounds.ymax),
    0.5 * (bounds.zmin + bounds.zmax),
]
distance = CAMERA_DISTANCE_SCALE * max(
    bounds.xmax - bounds.xmin,
    bounds.ymax - bounds.ymin,
    bounds.zmax - bounds.zmin,
)
axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
center[axis_index] = SECTION_VALUES[0]
eye = center.copy()
eye[axis_index] += distance
up = (1.0, 0.0, 0.0) if axis == "Y" else (0.0, 1.0, 0.0)

fv.view.set_perspective(False)
fv.camera.look_at(eye=tuple(eye), target=tuple(center), up=up)
fv.view.fit()
standard_view = fv.camera.get_state()
section_plane = getattr(section, f"{axis.lower()}_plane")

# Export every exact scalar at every requested position with fixed color ranges.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for scalar_name, color_range in SCALAR_EXPORTS:
    section.scalar_func = scalar_name
    section.colormap.min, section.colormap.max = color_range
    for section_value in SECTION_VALUES:
        section_plane.value = section_value
        fv.camera.set_state(standard_view)
        output_png = OUTPUT_DIR / f"{axis}_{section_value:g}_{scalar_name}.png"
        fv.export_png(str(output_png))
        print(f"Saved: {output_png}")

"""Write transient coordinate-section XDB/XFN files.

How to use:
1. Edit only the clearly marked CUSTOMIZE block below.
2. Enter the exact FieldView loader and scalar-function names.
3. Select X, Y, or Z, set the section position, and choose the time range.
4. Execute this file inside FieldView. Incorrect names produce errors listing
   the exact loaders or scalar functions available for selection.

Each XDB has a same-basename XFN listing the scalar functions to store.
Output names follow SECTION_LABEL_AXIS_POSITION_TIME_STEP.xdb.
"""

from pathlib import Path

import fieldview as fv


# =============================================================================
# CUSTOMIZE FOR YOUR DATA -- EDIT THIS BLOCK
# =============================================================================

# 1) Data loading
# Use the exact function name found under fieldview.data, including "load_".
# Example for OpenFOAM direct: "load_openfoam_direct" with system/controlDict.
# This workflow requires a transient dataset and selects time steps after loading.
# A loader requiring separate grid/results files needs corresponding load arguments.
LOADER_NAME = "load_openfoam_direct"
INPUT_FILE = Path(r"***DataPath***")

# 2) Coordinate section
# SECTION_LABEL is used only in filenames; it is not a boundary or FieldView name.
# SECTION_AXIS accepts "X", "Y", or "Z". POSITION uses dataset coordinates.
SECTION_LABEL = "***YourSection***"
SECTION_AXIS = "Z"
SECTION_POSITION = 1.57

# 3) Exact scalar names
# PRESSURE_NAME and every SCALAR_NAMES entry must match ds.scalar_functions.
PRESSURE_NAME = "p"
CP_NAME = "Cp"

# These exact scalar functions are written into every XFN/XDB pair.
# Add or remove names here when different variables must be stored.
SCALAR_NAMES = (PRESSURE_NAME, CP_NAME)

# 4) Cp = (pressure - reference pressure) / (0.5 * density * velocity^2)
# If CP_NAME already exists, it is reused. For OpenFOAM kinematic pressure p/rho,
# keep REFERENCE_DENSITY = 1.0; use consistent density for dimensional pressure.
REFERENCE_PRESSURE = 0.0
REFERENCE_DENSITY = 1.0
REFERENCE_VELOCITY = 1.0

# 5) Time-list indices
# 0 is the first entry, -1 is the last, and SKIP=0 writes every time step.
# Example: FIRST_INDEX=0, LAST_INDEX=9, SKIP=1 writes indices 0, 2, 4, 6, 8.
FIRST_INDEX = 0
LAST_INDEX = -1
SKIP = 0

# 6) Display and output
CONTOUR_COUNT = 21

# XDB and XFN files are written directly into this folder.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Output" / "XDB"

# =============================================================================
# END CUSTOMIZATION -- THE WORKFLOW BELOW NORMALLY NEEDS NO EDITING
# =============================================================================

# Stop immediately if visible template placeholders have not been replaced.
for setting_name, setting_value in (
    ("INPUT_FILE", str(INPUT_FILE)),
    ("SECTION_LABEL", SECTION_LABEL),
):
    if "***" in setting_value:
        raise ValueError(f"Replace {setting_name} in the CUSTOMIZE block")

# Resolve and validate the named loader and common customization values.
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
if not SCALAR_NAMES:
    raise ValueError("SCALAR_NAMES must contain at least one exact scalar name")
if REFERENCE_DENSITY <= 0.0 or REFERENCE_VELOCITY <= 0.0:
    raise ValueError("Reference density and velocity must be greater than zero")
if SKIP < 0:
    raise ValueError("SKIP must be zero or greater")

axis = SECTION_AXIS.upper()
ds = data_loader(str(INPUT_FILE), transient=True)
info = ds.transient_info()
ds.set_transient(solution_time=info.solution_time_values[-1])

# Exact-name checks prevent a similarly named scalar being selected.
if PRESSURE_NAME not in ds.scalar_functions:
    raise RuntimeError(
        f"Scalar {PRESSURE_NAME!r} was not found. Available: {ds.scalar_functions}"
    )

# Create Cp only when it is requested but does not already exist.
# Coordinate sections are defined by a plane and need no boundary name.
if CP_NAME in SCALAR_NAMES and CP_NAME not in ds.scalar_functions:
    fv.formula.create(
        CP_NAME,
        (fv.formula.quantity(PRESSURE_NAME) - REFERENCE_PRESSURE)
        / (0.5 * REFERENCE_DENSITY * REFERENCE_VELOCITY**2),
    )

missing_scalars = [name for name in SCALAR_NAMES if name not in ds.scalar_functions]
if missing_scalars:
    raise RuntimeError(
        f"Scalars {missing_scalars} were not found. Available: {ds.scalar_functions}"
    )

# Create the selected coordinate plane at the configured position.
plane_by_axis = {
    "X": fv.constant.Plane.X,
    "Y": fv.constant.Plane.Y,
    "Z": fv.constant.Plane.Z,
}
fv.view.reset()
section = fv.vis.create_coord(
    ds,
    plane=plane_by_axis[axis],
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=SCALAR_NAMES[0],
    display_type=fv.constant.DisplayType.SMOOTH,
    contours=fv.constant.ContourColoring.BLACK,
    show_mesh=False,
    **{f"{axis.lower()}_plane": fv.RangedValue(value=SECTION_POSITION)},
)
section.colormap.name = fv.constant.ColormapName.SPECTRUM
section.colormap.filled_contour = True
section.colormap.num_contours = CONTOUR_COUNT

# LAST_INDEX is inclusive; SKIP is the number of time steps omitted between writes.
stop_index = None if LAST_INDEX == -1 else LAST_INDEX + 1
time_steps = info.time_step_values[FIRST_INDEX:stop_index:SKIP + 1]
if not time_steps:
    raise ValueError("The selected transient index range contains no time steps")

# FieldView reads scalar names from the same-basename XFN beside each XDB file.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
function_text = "\n".join(SCALAR_NAMES) + "\n"
file_prefix = f"{SECTION_LABEL}_{axis}_{SECTION_POSITION:g}_"
for time_step in time_steps:
    ds.set_transient(time_step=time_step)
    xdb_file = OUTPUT_DIR / f"{file_prefix}{time_step}.xdb"
    xdb_file.with_suffix(".xfn").write_text(function_text, encoding="utf-8")
    fv.fv_script(f'XDB_WRITE "{xdb_file}" NOTHRESHOLD')
    print(f"Saved: {xdb_file}")

print(f"Time steps written: {len(time_steps)}")

"""Write a transient sequence of boundary-surface XDB/XFN files.

How to use:
1. Edit only the clearly marked CUSTOMIZE block below.
2. Enter the exact FieldView loader, boundary, and scalar-function names.
3. Set FIRST_INDEX, LAST_INDEX, and SKIP for the required time range.
4. Execute this file inside FieldView. Incorrect names produce errors listing
   the exact loader, scalar, or boundary names available for selection.

Each XDB has a same-basename XFN file listing the scalar functions to store.
The output filenames are: BOUNDARY_NAME_TIME_STEP.xdb and matching .xfn files.
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

# 2) Exact dataset names
# BOUNDARY_NAME must exactly match one entry from ds.boundary_types.
# PRESSURE_NAME and every SCALAR_NAMES entry must match ds.scalar_functions.
BOUNDARY_NAME = "***YourBoundaryName***"
PRESSURE_NAME = "p"
CP_NAME = "Cp"

# These exact scalar functions are written into every XFN/XDB pair.
# Add or remove names here when different variables must be stored.
SCALAR_NAMES = (PRESSURE_NAME, CP_NAME)

# 3) Cp = (pressure - reference pressure) / (0.5 * density * velocity^2)
# If CP_NAME already exists, it is reused. For OpenFOAM kinematic pressure p/rho,
# keep REFERENCE_DENSITY = 1.0; use consistent density for dimensional pressure.
REFERENCE_PRESSURE = 0.0
REFERENCE_DENSITY = 1.0
REFERENCE_VELOCITY = 1.0

# 4) Time-list indices
# 0 is the first entry, -1 is the last, and SKIP=0 writes every time step.
# Example: FIRST_INDEX=0, LAST_INDEX=9, SKIP=1 writes indices 0, 2, 4, 6, 8.
FIRST_INDEX = 0
LAST_INDEX = -1
SKIP = 0

# 5) Display and output
CONTOUR_COUNT = 21

# XDB and XFN files are written directly into this folder.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Output" / "XDB"

# =============================================================================
# END CUSTOMIZATION -- THE WORKFLOW BELOW NORMALLY NEEDS NO EDITING
# =============================================================================

# Stop immediately if visible template placeholders have not been replaced.
for setting_name, setting_value in (
    ("INPUT_FILE", str(INPUT_FILE)),
    ("BOUNDARY_NAME", BOUNDARY_NAME),
):
    if "***" in setting_value:
        raise ValueError(f"Replace {setting_name} in the CUSTOMIZE block")

# Resolve and validate the named fieldview.data loader and common inputs.
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
if not SCALAR_NAMES:
    raise ValueError("SCALAR_NAMES must contain at least one exact scalar name")
if REFERENCE_DENSITY <= 0.0 or REFERENCE_VELOCITY <= 0.0:
    raise ValueError("Reference density and velocity must be greater than zero")
if SKIP < 0:
    raise ValueError("SKIP must be zero or greater")

ds = data_loader(str(INPUT_FILE), transient=True)
info = ds.transient_info()
ds.set_transient(solution_time=info.solution_time_values[-1])

# Exact-name checks prevent a similarly named scalar or boundary being selected.
if PRESSURE_NAME not in ds.scalar_functions:
    raise RuntimeError(
        f"Scalar {PRESSURE_NAME!r} was not found. Available: {ds.scalar_functions}"
    )
if BOUNDARY_NAME not in ds.boundary_types:
    raise RuntimeError(
        f"Boundary {BOUNDARY_NAME!r} was not found. Available: {ds.boundary_types}"
    )

# Create Cp only when it is requested but does not already exist.
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

# Store the exact boundary surface and requested scalar functions in each XDB.
fv.view.reset()
surface = fv.vis.create_boundary(
    ds,
    types=[BOUNDARY_NAME],
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=SCALAR_NAMES[0],
    display_type=fv.constant.DisplayType.SMOOTH,
    contours=fv.constant.ContourColoring.BLACK,
    show_mesh=False,
)
surface.colormap.name = fv.constant.ColormapName.SPECTRUM
surface.colormap.filled_contour = True
surface.colormap.num_contours = CONTOUR_COUNT

# LAST_INDEX is inclusive; SKIP is the number of time steps omitted between writes.
stop_index = None if LAST_INDEX == -1 else LAST_INDEX + 1
time_steps = info.time_step_values[FIRST_INDEX:stop_index:SKIP + 1]
if not time_steps:
    raise ValueError("The selected transient index range contains no time steps")

# FieldView reads scalar names from the same-basename XFN beside each XDB file.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
function_text = "\n".join(SCALAR_NAMES) + "\n"
for time_step in time_steps:
    ds.set_transient(time_step=time_step)
    xdb_file = OUTPUT_DIR / f"{BOUNDARY_NAME}_{time_step}.xdb"
    xdb_file.with_suffix(".xfn").write_text(function_text, encoding="utf-8")
    fv.fv_script(f'XDB_WRITE "{xdb_file}" NOTHRESHOLD')
    print(f"Saved: {xdb_file}")

print(f"Time steps written: {len(time_steps)}")

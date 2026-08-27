"""Export pressure and Cp PNGs on one dataset boundary.

How to use:
1. Edit only the clearly marked CUSTOMIZE block below.
2. Enter exact FieldView loader, scalar, and boundary names.
3. Execute this file inside FieldView. If a scalar or boundary name is wrong,
   the error message lists the exact names available in the loaded dataset.

The output filenames are: BOUNDARY_NAME_p.png and BOUNDARY_NAME_Cp.png.
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

# 2) Exact dataset names
# These values must exactly match ds.scalar_functions and ds.boundary_types.
PRESSURE_NAME = "p"
BOUNDARY_NAME = "***YourBoundaryName***"

# If this exact scalar exists, it is used. Otherwise, it is created below.
CP_NAME = "Cp"

# 3) Cp = (pressure - reference pressure) / (0.5 * density * velocity^2)
# For OpenFOAM kinematic pressure p/rho, keep REFERENCE_DENSITY = 1.0.
# For dimensional pressure, enter the consistent reference density and units.
REFERENCE_PRESSURE = 0.0
REFERENCE_DENSITY = 1.0
REFERENCE_VELOCITY = 1.0

# 4) Image appearance and output
# Fixed ranges make PNG colors comparable between datasets or time steps.
PRESSURE_RANGE = (-1.2, 0.6)
CP_RANGE = (-2.4, 1.2)
CONTOUR_COUNT = 21
LEGEND_LABEL_COUNT = 5
LEGEND_POSITION = (0.68, 0.88)

# This default creates an Outputs folder beside the Script folder.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Outputs"

# =============================================================================
# END CUSTOMIZATION -- THE WORKFLOW BELOW NORMALLY NEEDS NO EDITING
# =============================================================================


# Stop immediately if a visible template placeholder has not been replaced.
for setting_name, setting_value in (
    ("INPUT_FILE", str(INPUT_FILE)),
    ("BOUNDARY_NAME", BOUNDARY_NAME),
):
    if "***" in setting_value:
        raise ValueError(f"Replace {setting_name} in the CUSTOMIZE block")

# Resolve and validate the named fieldview.data loader.
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
if REFERENCE_DENSITY <= 0.0 or REFERENCE_VELOCITY <= 0.0:
    raise ValueError("Reference density and velocity must be greater than zero")

ds = data_loader(str(INPUT_FILE), transient=TRANSIENT)
if TRANSIENT:
    final_time = ds.transient_info().solution_time_values[-1]
    ds.set_transient(solution_time=final_time)

# Exact-name checks prevent a similarly named scalar or boundary being selected.
if PRESSURE_NAME not in ds.scalar_functions:
    raise RuntimeError(
        f"Scalar {PRESSURE_NAME!r} was not found. Available: {ds.scalar_functions}"
    )
if BOUNDARY_NAME not in ds.boundary_types:
    raise RuntimeError(
        f"Boundary {BOUNDARY_NAME!r} was not found. Available: {ds.boundary_types}"
    )

# Reuse an existing Cp scalar, or create it from the configured pressure scalar.
if CP_NAME in ds.scalar_functions:
    cp_name = CP_NAME
else:
    cp_name = fv.formula.create(
        CP_NAME,
        (fv.formula.quantity(PRESSURE_NAME) - REFERENCE_PRESSURE)
        / (0.5 * REFERENCE_DENSITY * REFERENCE_VELOCITY**2),
    ).name

# Create one smooth, scalar-colored surface for the exact boundary name.
fv.view.reset()
surface = fv.vis.create_boundary(
    ds,
    types=[BOUNDARY_NAME],
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func=PRESSURE_NAME,
    display_type=fv.constant.DisplayType.SMOOTH,
    contours=fv.constant.ContourColoring.BLACK,
    show_mesh=False,
)
surface.colormap.name = fv.constant.ColormapName.SPECTRUM
surface.colormap.filled_contour = True
surface.colormap.use_local = False
surface.colormap.num_contours = CONTOUR_COUNT
surface.legend.show = True
surface.legend.spectrum.colorbar = True
surface.legend.spectrum.num_labels = LEGEND_LABEL_COUNT
surface.legend.relative_position = LEGEND_POSITION
fv.view.set_outline(False)
fv.view.set_perspective(False)
fv.view.fit()

# Export pressure and Cp with the same camera and configured fixed ranges.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for label, scalar_name, color_range in (
    ("p", PRESSURE_NAME, PRESSURE_RANGE),
    ("Cp", cp_name, CP_RANGE),
):
    output_png = OUTPUT_DIR / f"{BOUNDARY_NAME}_{label}.png"
    surface.scalar_func = scalar_name
    surface.colormap.min, surface.colormap.max = color_range
    fv.export_png(str(output_png))
    print(f"Saved: {output_png}")

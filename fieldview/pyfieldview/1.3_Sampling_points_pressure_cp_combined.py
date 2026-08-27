"""Sample pressure and Cp at user-specified XYZ coordinates.

How to use:
1. Edit only the clearly marked CUSTOMIZE block below.
2. Put one ``X Y Z`` point per line in POINTS_FILE. Commas, spaces, blank lines,
   and comments beginning with ``#`` are accepted.
3. Enter the exact FieldView loader and pressure-scalar names.
4. Execute this file inside FieldView. An incorrect scalar name produces an
   error listing the exact scalar functions available in the loaded dataset.

The output is a tab-separated text table containing requested coordinates,
probe status, actual sampled coordinates, pressure, and Cp.
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

# 2) Input points and output table
# POINTS_FILE is beside this script. Replace it with any absolute Path if needed.
POINTS_FILE = Path(__file__).resolve().with_name("coordinate_points.txt")

# This output is in ../Output, so it does not overwrite the input points file.
# Change the final filename if a more descriptive result name is preferred.
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "Output" / (
    "coordinate_points.txt"
)

# 3) Exact scalar names
# PRESSURE_NAME must exactly match one entry from ds.scalar_functions.
PRESSURE_NAME = "p"

# If this exact scalar exists, it is used. Otherwise, it is created below.
CP_NAME = "Cp"

# 4) Cp = (pressure - reference pressure) / (0.5 * density * velocity^2)
# For OpenFOAM kinematic pressure p/rho, keep REFERENCE_DENSITY = 1.0.
# For dimensional pressure, enter the consistent reference density and units.
REFERENCE_PRESSURE = 0.0
REFERENCE_DENSITY = 1.0
REFERENCE_VELOCITY = 1.0

# =============================================================================
# END CUSTOMIZATION -- THE WORKFLOW BELOW NORMALLY NEEDS NO EDITING
# =============================================================================


def read_points(path: Path) -> list[tuple[float, float, float]]:
    """Read comma- or whitespace-separated XYZ coordinates, ignoring comments."""
    points: list[tuple[float, float, float]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        values = raw_line.split("#", maxsplit=1)[0].replace(",", " ").split()
        if not values:
            continue
        if len(values) != 3:
            raise ValueError(f"{path.name}, line {line_number}: expected X Y Z")
        x, y, z = (float(value) for value in values)
        points.append((x, y, z))
    if not points:
        raise ValueError(f"No coordinate points were found in {path}")
    return points


def text_value(value: float | None) -> str:
    """Format one sampled value for the output table."""
    return "NaN" if value is None else f"{value:.12g}"


# Stop immediately if the visible input-path placeholder was not replaced.
if "***" in str(INPUT_FILE):
    raise ValueError("Replace INPUT_FILE in the CUSTOMIZE block")

# Resolve and validate the named fieldview.data loader and input files.
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
if not POINTS_FILE.is_file():
    raise FileNotFoundError(f"Coordinate file was not found: {POINTS_FILE}")
if REFERENCE_DENSITY <= 0.0 or REFERENCE_VELOCITY <= 0.0:
    raise ValueError("Reference density and velocity must be greater than zero")

ds = data_loader(str(INPUT_FILE), transient=TRANSIENT)
if TRANSIENT:
    solution_time = ds.transient_info().solution_time_values[-1]
    ds.set_transient(solution_time=solution_time)
    solution_label = f"{solution_time:g}"
else:
    solution_label = "steady"

if PRESSURE_NAME not in ds.scalar_functions:
    raise RuntimeError(
        f"Scalar {PRESSURE_NAME!r} was not found. Available: {ds.scalar_functions}"
    )

# Reuse an existing Cp scalar, or create it from the configured pressure scalar.
# Coordinate probes sample XYZ locations directly and need no boundary name.
if CP_NAME in ds.scalar_functions:
    cp_name = CP_NAME
else:
    cp_name = fv.formula.create(
        CP_NAME,
        (fv.formula.quantity(PRESSURE_NAME) - REFERENCE_PRESSURE)
        / (0.5 * REFERENCE_DENSITY * REFERENCE_VELOCITY**2),
    ).name

# Probe p and Cp at each requested displayed-space XYZ coordinate.
points = read_points(POINTS_FILE)
rows = [
    "Point\tRequested_X\tRequested_Y\tRequested_Z\t"
    f"Status\tSampled_X\tSampled_Y\tSampled_Z\t{PRESSURE_NAME}\t{cp_name}"
]
for point_number, point in enumerate(points, start=1):
    pressure_probe = fv.data.probe(point, dataset=ds, scalar_func=PRESSURE_NAME)
    cp_probe = fv.data.probe(point, dataset=ds, scalar_func=cp_name)
    hit = pressure_probe.hit and cp_probe.hit
    sampled_point = pressure_probe.point if hit else None
    sampled_xyz = (
        (
            text_value(sampled_point.x),
            text_value(sampled_point.y),
            text_value(sampled_point.z),
        )
        if sampled_point is not None
        else ("NaN", "NaN", "NaN")
    )
    rows.append(
        "\t".join(
            (
                str(point_number),
                *(f"{coordinate:.12g}" for coordinate in point),
                "HIT" if hit else "MISS",
                *sampled_xyz,
                text_value(pressure_probe.scalar.value),
                text_value(cp_probe.scalar.value),
            )
        )
    )

# Write one tab-separated table containing both scalar values.
header = [
    "# Pressure and Cp sampled at configured coordinates",
    f"# Input data: {INPUT_FILE}",
    f"# Solution time: {solution_label}",
    f"# Input points: {POINTS_FILE}",
    f"# Cp = ({PRESSURE_NAME} - {REFERENCE_PRESSURE:g}) / "
    f"(0.5 * {REFERENCE_DENSITY:g} * {REFERENCE_VELOCITY:g}^2)",
]
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join((*header, *rows)) + "\n", encoding="utf-8")

print(f"Points read: {len(points)}")
print(f"Saved: {OUTPUT_FILE}")

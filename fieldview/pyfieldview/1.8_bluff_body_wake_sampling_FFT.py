"""Sample a 2D wake region behind a bluff body for separate temporal FFT analysis.

PURPOSE: Generalize the fixed-point cylinder-wake sampling workflow to cars,
trucks, and other bluff bodies without assuming a body shape or solver.
The body-rear plane and freestream direction define "downstream"; the selected
rectangle must be strictly behind that plane. Geometry is NOT auto-detected.

HOW TO USE
1. Complete CUSTOMIZE FOR YOUR DATA below. All coordinates use dataset length
   units and the displayed FieldView coordinate system.
2. Run in FieldView: Tools > Execute Python File (its Python needs NumPy).
3. This file writes section_samples.npz and optionally fieldview_section.png.
4. Run the existing section_fft_analysis.py OUTSIDE FieldView using standalone
   Python with NumPy and Matplotlib, passing the new archive path:
     python section_fft_analysis.py "path/to/BluffBodyWakeFFT/section_samples.npz"
   FFT frequency-band, figure, and optional St=f*L/U controls are in that file.

No cylinder dimensions, body drawing, case path, exact field names, or local
Python installation are preselected. No boundary name is required. Sampling
and FFT stay separate; this script does not import or launch the FFT script.
"""

from pathlib import Path
import json
import os
import sys


# =============================================================================
# CUSTOMIZE FOR YOUR DATA -- EDIT ONLY THIS PARAMETER BLOCK
# =============================================================================
# A. DATA READER
# Exact function name under fieldview.data, including "load_".
# Examples: "load_openfoam_direct", "load_fvuns", "load_plot3d".
# Choose by FILE FORMAT; another solver may export a common format such as FV-UNS.
LOADER_NAME = "REPLACE_WITH_LOADER_NAME"
# Positional file arguments, in the order required by the documented loader.
# One-file reader: (Path(r"full input path"),)
# Grid + results reader: (Path(r"grid path"), Path(r"results path"))
INPUT_FILES = (Path(r"REPLACE_WITH_INPUT_FILE"),)
# Documented keyword arguments for your reader. This analysis needs transient data.
# Add reader-specific settings here; not every load_* reader has the same signature.
LOADER_OPTIONS: dict[str, object] = {"transient": True}
# First-time setup: True loads data, prints scalar/vector names, then stops.
LIST_NAMES_ONLY = False

# B. SAMPLING OUTPUT
# Absolute or script-relative directory; identical output names are overwritten.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Output" / "BluffBodyWakeFFT"

# C. BODY REAR AND FLOW DIRECTION -- no diameter or body shape is assumed.
# FLOW_AXIS is the global freestream axis, NOT the locally reversed wake velocity.
# FLOW_SIGN=+1 means +axis flow; -1 means -axis flow. This version is axis-aligned;
# for yawed flow, align the data first or use a projected-plane sampling workflow.
FLOW_AXIS = "X"
FLOW_SIGN = 1
# Absolute coordinate of the body's downstream-most extent along FLOW_AXIS.
# +X example: maximum body X (car rear); -X example: minimum body X.
# This is a rear reference PLANE, not the body centre or a reference length.
BODY_REAR_POSITION: float | None = None

# D. WAKE SECTION -- all bounds are ABSOLUTE dataset coordinates, not rear offsets.
# SECTION_AXIS is the normal axis. A and B are the two in-plane global axes:
# normal X -> A=Y, B=Z; normal Y -> A=X, B=Z; normal Z -> A=X, B=Y.
# For a car with streamwise X, lateral Y and vertical Z:
#   Z-normal: horizontal XY wake slice at the selected height.
#   Y-normal: vertical XZ wake slice at the selected lateral position.
#   X-normal: transverse YZ wake plane at a downstream station.
# Set the rectangle entirely behind BODY_REAR_POSITION, within the fluid domain;
# keep it clear of the ground, solid geometry, and unrelated downstream bodies.
# For +X flow on a Z-normal slice, WAKE_A_RANGE's minimum must exceed body rear X.
# For +X flow on an X-normal slice, SECTION_POSITION must exceed body rear X.
SECTION_AXIS = "Z"
SECTION_POSITION: float | None = None
WAKE_A_RANGE: tuple[float, float] | None = None
WAKE_B_RANGE: tuple[float, float] | None = None
# Uniform interpolated probe locations, NOT native CFD mesh nodes or cells.
# Total locations = NA * NB = 8,586. Runtime grows with locations * saved times.
# Spacing A=(Amax-Amin)/(NA-1); B=(Bmax-Bmin)/(NB-1).
# More spatial samples do not improve temporal frequency resolution.
NA, NB = 106, 81

# E. SIGNAL -- choose exactly one scalar or one vector component.
# "scalar": use SCALAR_NAME; "vector_component": use VECTOR_NAME and COMPONENT.
SIGNAL_KIND = "vector_component"
SCALAR_NAME = "REPLACE_WITH_SCALAR_NAME"
VECTOR_NAME = "REPLACE_WITH_VECTOR_NAME"
COMPONENT = "Y"  # X, Y, or Z in global coordinates, independent of section normal.
SIGNAL_UNITS = "REPLACE_WITH_UNITS"  # Label only; does not convert the signal.
# For wake asymmetry, select a lateral/vertical velocity component as appropriate.
# A scalar (e.g. pressure) is also supported; no Cp or pressure conversion is assumed.
# Optional full-section FieldView PNG, colored by PREVIEW_SCALAR_NAME.
# The analysis figure always shows the selected rectangle; native preview is full-section.
EXPORT_FIELDVIEW_PNG = False
PREVIEW_SCALAR_NAME = "REPLACE_WITH_PREVIEW_SCALAR"

# F. SAMPLING TIMES
# Inclusive limits in ORIGINAL solver solution-time units; None uses first/last.
# Prefer a statistically settled interval. All saved times within it are sampled.
TIME_START: float | None = None
TIME_END: float | None = None
# Multiply raw solution times by this factor to obtain seconds, e.g. 0.001 for ms.
# If time is nondimensional, supply the physical time scale before reporting Hz.
TIME_TO_SECONDS = 1.0
MIN_SAMPLES = 8  # Minimum to proceed, not a guarantee of sufficient record length.
UNIFORM_TIME_RTOL = 1e-5  # Irregular output spacing is rejected, never interpolated.
# =============================================================================
# END CUSTOMIZATION -- PROCESSING CODE BELOW
# =============================================================================

# Register the embedded Python runtime's DLL location when using Windows.
if sys.platform == "win32":
    python_dll_directory = os.add_dll_directory(sys.prefix)
import numpy as np
from numpy.typing import NDArray


def time_interval(times: NDArray[np.float64], minimum: int, tolerance: float) -> float:
    """Check uniform increasing physical times before probing or Fourier analysis."""
    if times.ndim != 1 or minimum < 4 or len(times) < minimum or not np.isfinite(times).all():
        raise ValueError(f"Need at least {minimum} finite times; minimum must be >= 4")
    intervals = np.diff(times)
    dt = float(intervals.mean())
    if dt <= 0 or not np.allclose(intervals, dt, rtol=tolerance, atol=abs(dt) * 1e-10):
        raise ValueError("Saved times must increase uniformly. No automatic resampling is performed")
    return dt


def section_points(axis: str, position: float, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Build Cartesian XYZ locations, ordered by B rows then A columns."""
    aa, bb = np.meshgrid(a, b, indexing="xy")
    normal = "XYZ".index(axis)
    in_plane = [i for i in range(3) if i != normal]
    points = np.full((aa.size, 3), position, dtype=float)
    points[:, in_plane[0]], points[:, in_plane[1]] = aa.ravel(), bb.ravel()
    return points


def check_wake_region(points: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return downstream distances and reject points on/upstream of the rear plane."""
    flow_axis = FLOW_AXIS.upper()
    if flow_axis not in {"X", "Y", "Z"} or FLOW_SIGN not in {-1, 1}:
        raise ValueError("FLOW_AXIS must be X/Y/Z and FLOW_SIGN must be +1 or -1")
    if BODY_REAR_POSITION is None or not np.isfinite(BODY_REAR_POSITION):
        raise ValueError("Set BODY_REAR_POSITION to the body's downstream-most coordinate")
    distance = FLOW_SIGN * (points[:, "XYZ".index(flow_axis)] - BODY_REAR_POSITION)
    if not np.isfinite(distance).all() or np.any(distance <= 0):
        raise ValueError(
            "The complete wake rectangle must be strictly downstream of the body rear. "
            "Check flow direction, rear position, section position, and wake limits."
        )
    return distance


def sample_section() -> None:
    """Load transient data and export fixed-point histories in a bluff-body wake."""
    import fieldview as fv

    loader = getattr(fv.data, LOADER_NAME, None)
    if not LOADER_NAME.startswith("load_") or not callable(loader):
        available = [name for name in dir(fv.data) if name.startswith("load_")]
        raise ValueError(f"Set LOADER_NAME. Available loader names: {available}")
    script_dir = Path(__file__).resolve().parent
    files = [(script_dir / path).resolve() for path in INPUT_FILES]
    output_dir = (script_dir / OUTPUT_DIR).resolve()
    if not files or any(not path.is_file() for path in files):
        raise FileNotFoundError("Set INPUT_FILES to existing reader input files in the correct order")
    ds = loader(*(str(path) for path in files), **LOADER_OPTIONS)
    if LIST_NAMES_ONLY:
        print("Scalar names:", ds.scalar_functions)
        print("Vector names:", ds.vector_functions)
        return
    axis, component = SECTION_AXIS.upper(), COMPONENT.upper()
    if axis not in {"X", "Y", "Z"} or component not in {"X", "Y", "Z"}:
        raise ValueError("SECTION_AXIS and COMPONENT must be X, Y, or Z")
    if SECTION_POSITION is None or not np.isfinite(SECTION_POSITION):
        raise ValueError("Set SECTION_POSITION to a finite coordinate")
    for label, limits in (("WAKE_A_RANGE", WAKE_A_RANGE), ("WAKE_B_RANGE", WAKE_B_RANGE)):
        if limits is None or len(limits) != 2 or not np.isfinite(limits).all() or limits[0] >= limits[1]:
            raise ValueError(f"Set {label} to increasing (minimum, maximum) coordinates")
    if any(not isinstance(n, int) or n < 2 for n in (NA, NB)):
        raise ValueError("NA and NB must be integers >= 2")
    if not np.isfinite(TIME_TO_SECONDS) or TIME_TO_SECONDS <= 0:
        raise ValueError("TIME_TO_SECONDS must be a positive conversion to seconds")
    if SIGNAL_KIND == "scalar":
        name, available = SCALAR_NAME, ds.scalar_functions
    elif SIGNAL_KIND == "vector_component":
        name, available = VECTOR_NAME, ds.vector_functions
    else:
        raise ValueError("SIGNAL_KIND must be scalar or vector_component")
    if name not in available:
        raise ValueError(f"Signal {name!r} not found. Exact available names: {available}")
    if EXPORT_FIELDVIEW_PNG and PREVIEW_SCALAR_NAME not in ds.scalar_functions:
        raise ValueError(f"Set PREVIEW_SCALAR_NAME from {ds.scalar_functions}")

    info = ds.transient_info()
    raw_times = np.asarray(info.solution_time_values, dtype=float)
    steps = np.asarray(info.time_step_values)
    if len(steps) != len(raw_times):
        raise ValueError("Transient time-step and solution-time lists do not match")
    selected = np.ones(len(raw_times), dtype=bool)
    if TIME_START is not None:
        selected &= raw_times >= TIME_START
    if TIME_END is not None:
        selected &= raw_times <= TIME_END
    raw_times, steps = raw_times[selected], steps[selected]
    times = raw_times * TIME_TO_SECONDS
    dt = time_interval(times, MIN_SAMPLES, UNIFORM_TIME_RTOL)
    a, b = np.linspace(*WAKE_A_RANGE, NA), np.linspace(*WAKE_B_RANGE, NB)
    points = section_points(axis, SECTION_POSITION, a, b)
    downstream = check_wake_region(points)
    values = np.full((len(times), len(points)), np.nan)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(points)} locations x {len(times)} times; dt={dt:g} s", flush=True)

    # Fixed locations give Eulerian histories. A miss remains NaN, never zero.
    for row, step in enumerate(steps):
        ds.set_transient(time_step=int(step))
        for column, point in enumerate(points):
            xyz = tuple(float(value) for value in point)
            if SIGNAL_KIND == "scalar":
                probe = fv.data.probe(xyz, dataset=ds, scalar_func=name)
                value = probe.scalar.value
            else:
                probe = fv.data.probe(xyz, dataset=ds, vector_func=name)
                vector = probe.vector.value
                value = getattr(vector, component.lower()) if vector is not None else None
            if probe.hit and value is not None:
                values[row, column] = value
        print(f"Sampled {row + 1}/{len(times)}, raw time={raw_times[row]:g}", flush=True)

    # Save geometry and units with the samples; FFT choices belong to the other script.
    metadata = dict(
        loader=LOADER_NAME, input_files=[str(path) for path in files],
        section_axis=axis, section_position=SECTION_POSITION,
        signal=name if SIGNAL_KIND == "scalar" else f"{name}.{component.lower()}",
        units=SIGNAL_UNITS, time_to_seconds=TIME_TO_SECONDS,
        region="bluff-body wake", flow_axis=FLOW_AXIS.upper(), flow_sign=FLOW_SIGN,
        body_rear_position=BODY_REAR_POSITION,
        downstream_range=[float(downstream.min()), float(downstream.max())],
    )
    archive = output_dir / "section_samples.npz"
    np.savez_compressed(archive, times=times, raw_times=raw_times, time_steps=steps,
                        points=points, values=values, a=a, b=b, metadata=json.dumps(metadata))
    valid = np.isfinite(values).all(axis=0)
    print(f"Complete wake histories: {valid.sum()}/{len(points)}", flush=True)
    if not valid.any():
        raise ValueError(f"No complete wake histories; inspect region and signal. Saved: {archive}")
    if EXPORT_FIELDVIEW_PNG:
        fv.view.reset()
        fv.vis.create_coord(
            ds, plane=getattr(fv.constant.Plane, axis),
            coloring=fv.constant.Coloring.SCALAR, scalar_func=PREVIEW_SCALAR_NAME,
            display_type=fv.constant.DisplayType.SMOOTH, show_mesh=False,
            **{f"{axis.lower()}_plane": fv.RangedValue(value=SECTION_POSITION)},
        )
        center = points.mean(axis=0)
        eye = center.copy()
        eye["XYZ".index(axis)] += 3 * max(np.ptp(a), np.ptp(b))
        up = (1., 0., 0.) if axis == "Y" else (0., 1., 0.)
        fv.view.set_perspective(False)
        fv.camera.look_at(eye=tuple(eye), target=tuple(center), up=up)
        fv.view.fit()
        fv.export_png(str(output_dir / "fieldview_section.png"))
    print(f"Saved samples: {archive}", flush=True)


if __name__ == "__main__":
    sample_section()

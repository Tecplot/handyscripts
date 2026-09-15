"""PURPOSE: Sample a bluff-body wake in FieldView and automatically analyze its FFT.

HOW TO USE
1. Edit the CUSTOMIZE block; active settings match the OpenFOAM cylinder01 case.
2. Run this file in FieldView: Tools > Execute Python File (NumPy required).
3. Sampling writes section_samples.npz and the optional FieldView preview.
4. ANALYSIS_PYTHON runs this same file with --analyze in a separate process,
   producing section_fft.png, section_spectra.npz, section_spectrum.txt, and
   section_fft_summary.txt beside the archive. Existing outputs are replaced.

This file contains both stages; neither original script is required at runtime.
Matplotlib loads only in the analysis process to avoid FieldView DLL conflicts.
ANALYSIS_PYTHON must have NumPy and Matplotlib; change its path for another PC.
To reanalyze an archive outside FieldView without resampling:
    python -E 1.8_bluff_body_wake_sampling_FFT_combined.py --analyze "C:/path/section_samples.npz"
The body's rear plane and flow direction define downstream; geometry is not
inferred. All sampling coordinates use dataset units. TIME_TO_SECONDS converts
saved solution times to seconds before FFT; reference length/speed use m and m/s.
"""

from pathlib import Path
import json
import os
import sys
import subprocess

# Store the absolute path before FieldView can change the working directory.
SCRIPT_PATH = Path(__file__).resolve()


# =============================================================================
# CUSTOMIZE FOR YOUR DATA -- EDIT ONLY THIS PARAMETER BLOCK
# Commented assignment = general input; the next line = OpenFOAM cylinder01.
# Identical values are repeated to show the case setting for every input.
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
OUTPUT_DIR = SCRIPT_PATH.parent.parent / "Output" / "BluffBodyWakeFFT"

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
# SIGNAL_UNITS = "REPLACE_WITH_UNITS"  # Label only; does not convert the signal.
SIGNAL_UNITS = "m/s"  # Units of U.y.
# For wake asymmetry, select a lateral/vertical velocity component as appropriate.
# A scalar (e.g. pressure) is also supported; no Cp or pressure conversion is assumed.
# Optional full-section FieldView PNG, colored by PREVIEW_SCALAR_NAME.
# The analysis figure always shows the selected rectangle; native preview is full-section.
# EXPORT_FIELDVIEW_PNG = False
EXPORT_FIELDVIEW_PNG = True
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
# G. AUTOMATIC FFT ANALYSIS -- standalone Python with NumPy and Matplotlib.
ANALYSIS_PYTHON = Path(r"REPLACE_WITH_PYTHON_EXECUTABLE")
# Python 3.12 is configured because this PC's Python 3.14 lacks Matplotlib.
FREQUENCY_MIN = 0.0  # Hz; exclude DC even when this is zero.
FREQUENCY_MAX: float | None = None  # Hz; None includes all positive bins.
REFERENCE_LENGTH: float | None = None  # None disables Strouhal reporting.
REFERENCE_VELOCITY: float | None = None
FIGURE_SIZE = (12, 8)
FIGURE_DPI = 180
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


def sample_section() -> Path | None:
    """Load transient data and export fixed-point histories in a bluff-body wake."""
    import fieldview as fv

    loader = getattr(fv.data, LOADER_NAME, None)
    if not LOADER_NAME.startswith("load_") or not callable(loader):
        available = [name for name in dir(fv.data) if name.startswith("load_")]
        raise ValueError(f"Set LOADER_NAME. Available loader names: {available}")
    script_dir = SCRIPT_PATH.parent
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

    # Save geometry and units with the samples for the analysis process.
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
    return archive


def temporal_psd(
    times: NDArray[np.float64], values: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return Hz and one-sided Hann PSD for complete histories (time, point)."""
    if times.ndim != 1 or len(times) < max(4, MIN_SAMPLES) or not np.isfinite(times).all():
        raise ValueError(f"Need at least {max(4, MIN_SAMPLES)} finite saved times")
    intervals = np.diff(times)
    dt = float(intervals.mean())
    if dt <= 0 or not np.allclose(intervals, dt, rtol=UNIFORM_TIME_RTOL, atol=abs(dt) * 1e-10):
        raise ValueError("Saved times must increase uniformly; no resampling is performed")
    if values.ndim != 2 or values.shape[0] != len(times) or not np.isfinite(values).all():
        raise ValueError("Signals must have shape (time, point) with finite values")
    count = len(times)
    window = np.hanning(count + 1)[:-1]
    fluctuations = values - values.mean(axis=0, keepdims=True)
    transform = np.fft.rfft(fluctuations * window[:, None], axis=0)
    psd = np.abs(transform) ** 2 * dt / np.sum(window**2)
    psd[1:-1 if count % 2 == 0 else None] *= 2.0
    return np.fft.rfftfreq(count, d=dt), psd


def analyze(samples_file: Path) -> None:
    """Read the sampling archive and export spectra, a section plot, and a report."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Read fixed-point histories; exclude points missing any saved time.
    with np.load(samples_file, allow_pickle=False) as data:
        times = np.asarray(data["times"], dtype=float)
        points = np.asarray(data["points"], dtype=float)
        values = np.asarray(data["values"], dtype=float)
        a, b = np.asarray(data["a"], dtype=float), np.asarray(data["b"], dtype=float)
        metadata = json.loads(str(data["metadata"].item()))
    if values.shape != (len(times), len(a) * len(b)) or points.shape != (len(a) * len(b), 3):
        raise ValueError("Archive geometry and signal dimensions do not match")
    valid = np.isfinite(values).all(axis=0)
    if not valid.any():
        raise ValueError("No point has a complete finite time history")

    # Average local powers, preserving fluctuations that cancel in a spatial mean.
    frequencies, psd = temporal_psd(times, values[:, valid])
    mean_psd = psd.mean(axis=1)
    band = (frequencies > 0) & (frequencies >= FREQUENCY_MIN)
    if FREQUENCY_MAX is not None:
        band &= frequencies <= FREQUENCY_MAX
    if not band.any():
        raise ValueError("The frequency band contains no positive FFT bins")
    bins = np.flatnonzero(band)
    peak_bin = bins[np.argmax(mean_psd[band])]
    if mean_psd[peak_bin] <= 0:
        raise ValueError("No fluctuating energy in the selected frequency band")
    peak = float(frequencies[peak_bin])
    local_peak = frequencies[bins[np.argmax(psd[band], axis=0)]]
    rms = values[:, valid].std(axis=0)
    local_peak[rms == 0] = np.nan
    representative = np.flatnonzero(valid)[np.argmax(psd[peak_bin])]
    strouhal: float | None = None
    if REFERENCE_LENGTH is not None and REFERENCE_VELOCITY is not None:
        if not np.isfinite([REFERENCE_LENGTH, REFERENCE_VELOCITY]).all() or min(REFERENCE_LENGTH, REFERENCE_VELOCITY) <= 0:
            raise ValueError("Strouhal reference length and speed must be finite and positive")
        strouhal = peak * REFERENCE_LENGTH / REFERENCE_VELOCITY

    # Plot in the archive's actual section axes; no body geometry is assumed.
    axis = metadata["section_axis"].upper()
    labels = [label for label in "XYZ" if label != axis]
    signal, units = metadata["signal"], metadata["units"]
    peak_map = np.full(len(points), np.nan)
    peak_map[valid] = local_peak
    fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE, constrained_layout=True)
    plot = axes[0, 0].pcolormesh(a, b, values[-1].reshape(len(b), len(a)), shading="auto", cmap="coolwarm")
    fig.colorbar(plot, ax=axes[0, 0], label=f"{signal} [{units}]")
    axes[0, 0].set_title(f"Signal at t={times[-1]:g} s")
    plot = axes[0, 1].pcolormesh(a, b, peak_map.reshape(len(b), len(a)), shading="auto", vmin=0, vmax=frequencies[-1])
    fig.colorbar(plot, ax=axes[0, 1], label="Peak frequency [Hz]")
    axes[0, 1].set_title("Local peak-frequency bin")
    for ax in axes[0]:
        ax.set(xlabel=labels[0], ylabel=labels[1], aspect="equal")
    axes[1, 0].plot(times, values[:, representative])
    axes[1, 0].set(title=f"Strongest point at common peak: {points[representative]}", xlabel="Time [s]", ylabel=f"{signal} [{units}]")
    axes[1, 1].plot(frequencies[1:], mean_psd[1:])
    axes[1, 1].axvline(peak, color="red", linestyle="--")
    title = f"Mean local PSD: f={peak:g} Hz"
    if strouhal is not None:
        title += f", St={strouhal:.4g}"
    axes[1, 1].set(title=title, xlabel="Frequency [Hz]", ylabel=f"PSD [({units})²/Hz]")
    fig.suptitle(f"Temporal FFT: {axis}={metadata['section_position']:g}, {signal}")
    output_dir = samples_file.resolve().parent
    fig.savefig(output_dir / "section_fft.png", dpi=FIGURE_DPI)
    plt.close(fig)

    # Save numerical results and the sampling limits needed to interpret the peak.
    np.savez_compressed(
        output_dir / "section_spectra.npz", frequencies=frequencies, psd=psd,
        mean_psd=mean_psd, points=points[valid], valid=valid, a=a, b=b,
        local_peak_frequency=local_peak, rms=rms, peak_frequency=peak,
        strouhal=np.nan if strouhal is None else strouhal, metadata=json.dumps(metadata),
    )
    np.savetxt(output_dir / "section_spectrum.txt", np.column_stack((frequencies, mean_psd)),
               header=f"frequency_Hz mean_PSD_({units})^2_per_Hz")
    dt = float(np.diff(times).mean())
    report = (
        f"Samples: {samples_file.resolve()}\nSignal: {signal}; units: {units}\n"
        f"Time: {times[0]:g} to {times[-1]:g} s; samples: {len(times)}\n"
        f"Complete histories: {valid.sum()}/{len(valid)}\n"
        f"Snapshot interval: {dt:g} s; Nyquist: {0.5 / dt:g} Hz\n"
        f"FFT bin spacing: {1 / (len(times) * dt):g} Hz\n"
        f"Peak bin: {peak:g} Hz\n"
        f"Strouhal: {strouhal if strouhal is not None else 'disabled'}\n"
        f"Reference length: {REFERENCE_LENGTH}; reference speed: {REFERENCE_VELOCITY}\n"
        f"Observed cycles at peak: {(times[-1] - times[0]) * peak:g}\n"
        "Method: per-point mean removal, periodic Hann, one-sided PSD, mean local power.\n"
        "Incomplete histories excluded; irregular times rejected.\n"
        "Peak is a candidate shedding frequency; check record length and aliasing.\n"
    )
    (output_dir / "section_fft_summary.txt").write_text(report, encoding="utf-8")
    print(report)



def run() -> None:
    """Sample in FieldView, then run this file's analysis in standalone Python."""
    if not LIST_NAMES_ONLY and not ANALYSIS_PYTHON.is_file():
        raise FileNotFoundError(f"Set ANALYSIS_PYTHON to a Python with NumPy/Matplotlib: {ANALYSIS_PYTHON}")
    archive = sample_section()
    if archive is not None:
        subprocess.run(
            [str(ANALYSIS_PYTHON), "-E", str(SCRIPT_PATH), "--analyze", str(archive)],
            check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--analyze":
        if len(sys.argv) != 3:
            raise SystemExit("Usage: python combined_script.py --analyze SAMPLES.npz")
        analyze(Path(sys.argv[2]))
    else:
        run()

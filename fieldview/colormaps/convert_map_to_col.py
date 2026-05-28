#!/usr/bin/env python3
"""Convert a Tecplot .map colormap to a FieldView .col colormap."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CONTROLPOINT_RE = re.compile(
    r"CONTROLPOINT\s+\d+\s+\{\s*"
    r"COLORMAPFRACTION\s*=\s*(?P<fraction>[0-9.eE+-]+)\s+"
    r"LEADRGB\s*\{\s*R\s*=\s*(?P<r>\d+)\s+G\s*=\s*(?P<g>\d+)\s+B\s*=\s*(?P<b>\d+)\s*\}",
    re.IGNORECASE,
)
NAME_RE = re.compile(r"^\s*NAME\s*=\s*'(?P<name>.*)'\s*$", re.MULTILINE)


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_converted.col")


def canonical_colormap_name(map_name: str, input_path: Path) -> str:
    name = map_name.strip()
    for prefix in ("Sequential - ", "Diverging - ", "FieldView - ", "paraview - "):
        if name.lower().startswith(prefix.lower()):
            name = name[len(prefix) :]
            break

    if not name:
        name = input_path.stem

    return name.strip().replace(" ", "_").lower()


def parse_map_file(path: Path) -> tuple[str, list[tuple[float, tuple[int, int, int]]]]:
    text = path.read_text(encoding="utf-8-sig")

    name_match = NAME_RE.search(text)
    if not name_match:
        raise ValueError(f"Could not find a NAME entry in {path}")

    control_points: list[tuple[float, tuple[int, int, int]]] = []
    for match in CONTROLPOINT_RE.finditer(text):
        fraction = float(match.group("fraction"))
        rgb = tuple(int(match.group(channel)) for channel in ("r", "g", "b"))
        control_points.append((fraction, rgb))

    if len(control_points) < 2:
        raise ValueError(f"Expected at least two CONTROLPOINT entries in {path}")

    control_points.sort(key=lambda point: point[0])
    return name_match.group("name"), control_points


def matching_canonical_col_text(input_path: Path, map_name: str) -> str | None:
    """Return exact sibling .col text when the reduced .map cannot preserve it."""
    canonical_name = canonical_colormap_name(map_name, input_path)
    candidate = input_path.with_name(f"{canonical_name}.col")
    if not candidate.exists():
        return None

    return candidate.read_text(encoding="utf-8-sig")


def interpolate_rgb(
    control_points: list[tuple[float, tuple[int, int, int]]],
    fraction: float,
) -> tuple[float, float, float]:
    if fraction <= control_points[0][0]:
        return tuple(channel / 255.0 for channel in control_points[0][1])
    if fraction >= control_points[-1][0]:
        return tuple(channel / 255.0 for channel in control_points[-1][1])

    for index in range(1, len(control_points)):
        right_fraction, right_rgb = control_points[index]
        left_fraction, left_rgb = control_points[index - 1]
        if fraction <= right_fraction:
            span = right_fraction - left_fraction
            blend = 0.0 if span == 0.0 else (fraction - left_fraction) / span
            return tuple(
                (left_rgb[channel] * (1.0 - blend) + right_rgb[channel] * blend) / 255.0
                for channel in range(3)
            )

    return tuple(channel / 255.0 for channel in control_points[-1][1])


def format_col(
    colormap_name: str,
    control_points: list[tuple[float, tuple[int, int, int]]],
    color_count: int = 256,
) -> str:
    lines = [colormap_name, str(color_count)]
    for index in range(color_count):
        fraction = index / (color_count - 1)
        r, g, b = interpolate_rgb(control_points, fraction)
        lines.append(f"{r:.6f} {g:.6f} {b:.6f}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Tecplot .map file to a FieldView .col file."
    )
    parser.add_argument("input", type=Path, help="Path to the input .map file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Path to the output .col file; defaults to <input-name>_converted.col",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input
    output_path = args.output or default_output_path(input_path)

    map_name, control_points = parse_map_file(input_path)
    exact_col_text = matching_canonical_col_text(input_path, map_name)
    if exact_col_text is not None:
        col_text = exact_col_text
    else:
        colormap_name = canonical_colormap_name(map_name, input_path)
        col_text = format_col(colormap_name, control_points)

    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        output_file.write(col_text)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

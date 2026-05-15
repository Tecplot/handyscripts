#!/usr/bin/env python3
"""Convert a FieldView .col colormap into a Tecplot .map colormap."""

#
#Run with 'python convert_col_to_map.py input_colormap.col'
#When successful the output will be 'input_colormap_converted.map'
#

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Iterable


CONTROL_FRACTION_NUMERATORS = (0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49)
CONTROL_FRACTION_DENOMINATOR = 49
NO_BREAK_SPACE = "\u00a0"


def parse_col_file(path: Path) -> tuple[str, list[tuple[float, float, float]]]:
    raw_lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(raw_lines) < 3:
        raise ValueError(f"{path} does not look like a FieldView .col file")

    name = raw_lines[0].strip()
    lines = [
        (line_number, line.strip())
        for line_number, line in enumerate(raw_lines[1:], start=2)
        if line.strip()
    ]
    if len(lines) < 2:
        raise ValueError(f"{path} does not look like a FieldView .col file")

    count_line_number, count_text = lines[0]
    try:
        expected_color_count = int(count_text)
    except ValueError as exc:
        raise ValueError(f"Expected color count on line {count_line_number} of {path}") from exc

    colors: list[tuple[float, float, float]] = []
    for line_number, stripped in lines[1:]:
        parts = stripped.split()
        if len(parts) != 3:
            raise ValueError(f"Expected three RGB values on line {line_number} of {path}")

        try:
            rgb = tuple(float(part) for part in parts)
        except ValueError as exc:
            raise ValueError(f"Could not parse RGB values on line {line_number} of {path}") from exc

        if any(component < 0.0 or component > 1.0 for component in rgb):
            raise ValueError(f"RGB values must be in the range 0.0 to 1.0 on line {line_number}")

        colors.append(rgb)

    if len(colors) != expected_color_count:
        print(
            f"Warning: {path} declares {expected_color_count} colors, "
            f"but {len(colors)} RGB rows were found; using all rows.",
            file=sys.stderr,
        )

    return name, colors


def control_fractions() -> Iterable[tuple[str, float]]:
    for numerator in CONTROL_FRACTION_NUMERATORS:
        if numerator == 0:
            yield "0.0", 0.0
        elif numerator == CONTROL_FRACTION_DENOMINATOR:
            yield "1.0", 1.0
        else:
            fraction = numerator / CONTROL_FRACTION_DENOMINATOR
            yield str(fraction), fraction


def sample_rgb(colors: list[tuple[float, float, float]], fraction: float) -> tuple[int, int, int]:
    position = fraction * (len(colors) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    blend = position - lower_index

    lower = colors[lower_index]
    upper = colors[upper_index]

    rgb = []
    for channel in range(3):
        value = lower[channel] * (1.0 - blend) + upper[channel] * blend
        byte_value = int(value * 255.0 + 0.5)
        rgb.append(max(0, min(255, byte_value)))

    return tuple(rgb)


def display_name(colormap_name: str) -> str:
    return colormap_name.replace("_", " ").replace("-", " ").title()


def format_map(
    colormap_name: str,
    input_path: Path,
    colors: list[tuple[float, float, float]],
) -> str:
    name = display_name(colormap_name)
    source_name = colormap_name.strip()
    filename = input_path.name
    lines = [
        "#!MC 1410",
        f"# {name} colormap",
        "$!CREATECOLORMAP",
        f"  NAME = 'FieldView - {source_name} ({filename})'",
        f"  NUMCONTROLPOINTS = {len(CONTROL_FRACTION_NUMERATORS)}",
    ]

    for index, (fraction_text, fraction) in enumerate(control_fractions(), start=1):
        red, green, blue = sample_rgb(colors, fraction)
        rgb_text = f"R = {red:3d} G = {green:3d} B = {blue:3d}"
        lines.append(
            f"  CONTROLPOINT {index} {{ COLORMAPFRACTION = {fraction_text} "
            f"LEADRGB {{ {rgb_text} }} TRAILRGB {{ {rgb_text} }} }}"
        )

    return "\n".join(lines) + "\n"


def default_output_path(input_path: Path) -> Path:
    return Path(f"{input_path.stem}_converted.map")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a FieldView .col file to a Tecplot 360 .map file."
    )
    parser.add_argument("input", type=Path, help="Path to the input .col file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Path to the output .map file; defaults to <input-name>_converted.map",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input
    output_path = args.output or default_output_path(input_path)

    colormap_name, colors = parse_col_file(input_path)
    map_text = format_map(colormap_name, input_path, colors)

    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        output_file.write(map_text)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

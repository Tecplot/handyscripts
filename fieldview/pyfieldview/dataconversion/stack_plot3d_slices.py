#!/usr/bin/env python3
"""Stack formatted-ASCII PLOT3D cuts into one 3D PLOT3D volume.

PLOT3D 2D-Slice to 3D-Volume Converter developed by the Tecplot, Inc. Japan Support Team.

This utility converts multiple 2D or thin-slab PLOT3D datasets into
a single 3D structured PLOT3D dataset for use with FieldView.
This converter supports the PLOT3D variants needed for the present PIV case:

* single-grid files without a leading grid count;
* multi-grid files with a leading grid count, including a count of 1;
* 2D grids: I J followed by X and Y arrays;
* 3D thin-slab grids: I J K followed by X, Y, and Z arrays;
* matching PLOT3D function files with one or more nodal variables;
* optional input IBLANK arrays (read and discarded).

For a 3D thin-slab input such as I=40, J=60, K=2, the converter must reduce
that slab to one physical cut before stacking it with other files. Select a
source K plane explicitly with --source-k-index, or average all source K
planes with --source-k-average. The output K dimension is the number of cuts,
not the sum of the source K dimensions.

Output is one single-grid, formatted-ASCII 3D PLOT3D grid and, optionally, one
matching PLOT3D function file. No interpolation, registration, smoothing, or
vector rotation is performed.

Example command line execution for 3 pairs ().xyz and .fun) of source data files:
python .\stack_plot3d_slices_fixed.py
--grid-files ".\xyz1_-40.dat" ".\xyz1_-30.dat" ".\xyz1_-20.dat"
--function-files ".\output1_-40.fun" ".\output1_-30.fun" ".\output1_-20.fun"
--input-layout multi
--input-dimension 3d 
--input-organization whole
--source-k-index 1
--positions -40 -30 -20 
--plane xy
--output-grid ".\piv_3d.xyz"
--output-function ".\piv_3d.fun"

"""

from __future__ import annotations

import argparse
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


class Plot3DError(RuntimeError):
    """Raised when an input file does not match a supported PLOT3D layout."""


@dataclass(frozen=True)
class GridBlock:
    ni: int
    nj: int
    nk: int
    coordinates: tuple[list[float], ...]  # 2 arrays for 2D, 3 arrays for 3D
    source: Path
    block_index: int
    input_dimension: int
    layout: str
    organization: str

    @property
    def plane_size(self) -> int:
        return self.ni * self.nj

    @property
    def size(self) -> int:
        return self.ni * self.nj * self.nk


@dataclass(frozen=True)
class FunctionBlock:
    ni: int
    nj: int
    nk: int
    nvar: int
    values: list[list[float]]
    source: Path
    block_index: int
    input_dimension: int
    layout: str
    organization: str

    @property
    def plane_size(self) -> int:
        return self.ni * self.nj

    @property
    def size(self) -> int:
        return self.ni * self.nj * self.nk


@dataclass(frozen=True)
class GridCut:
    ni: int
    nj: int
    c1: list[float]
    c2: list[float]
    source: Path
    block_index: int
    source_nk: int
    reduction: str

    @property
    def size(self) -> int:
        return self.ni * self.nj


@dataclass(frozen=True)
class FunctionCut:
    ni: int
    nj: int
    nvar: int
    values: list[list[float]]
    source: Path
    block_index: int
    source_nk: int
    reduction: str

    @property
    def size(self) -> int:
        return self.ni * self.nj


def _read_tokens(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise Plot3DError(
            f"{path}: not a readable formatted-ASCII file. "
            "The input may be binary or Fortran-unformatted PLOT3D."
        ) from exc
    except OSError as exc:
        raise Plot3DError(f"Cannot read {path}: {exc}") from exc

    tokens = text.replace(",", " ").split()
    if not tokens:
        raise Plot3DError(f"{path}: file is empty")
    return tokens


def _as_float(token: str, *, path: Path) -> float:
    try:
        return float(token.replace("D", "E").replace("d", "e"))
    except ValueError as exc:
        raise Plot3DError(f"{path}: invalid numeric token {token!r}") from exc


def _as_positive_int(token: str, *, path: Path, label: str) -> int:
    value = _as_float(token, path=path)
    rounded = round(value)
    if not math.isfinite(value) or abs(value - rounded) > 1.0e-12 or rounded <= 0:
        raise Plot3DError(
            f"{path}: {label} must be a positive integer; found {token!r}"
        )
    return int(rounded)


def _take_floats(
    tokens: Sequence[str], start: int, count: int, *, path: Path, label: str
) -> tuple[list[float], int]:
    end = start + count
    if end > len(tokens):
        raise Plot3DError(
            f"{path}: insufficient values while reading {label}; "
            f"needed {count}, found {max(0, len(tokens) - start)}"
        )
    return [_as_float(token, path=path) for token in tokens[start:end]], end


def _parse_grid_single(
    tokens: Sequence[str],
    *,
    path: Path,
    dimension: int,
    organization: str,
    has_iblank: bool,
) -> list[GridBlock]:
    dim_count = 2 if dimension == 2 else 3
    if len(tokens) < dim_count:
        raise Plot3DError(f"{path}: missing {dimension}D grid dimensions")

    ni = _as_positive_int(tokens[0], path=path, label="I dimension")
    nj = _as_positive_int(tokens[1], path=path, label="J dimension")
    nk = (
        _as_positive_int(tokens[2], path=path, label="K dimension")
        if dimension == 3
        else 1
    )
    plane_size = ni * nj
    n = plane_size * nk
    index = dim_count
    labels = ("X", "Y") if dimension == 2 else ("X", "Y", "Z")

    coordinates: list[list[float]] = [[] for _ in labels]
    if dimension == 3 and organization == "planes":
        for k in range(1, nk + 1):
            for coord_index, label in enumerate(labels):
                array, index = _take_floats(
                    tokens,
                    index,
                    plane_size,
                    path=path,
                    label=f"K={k} {label} coordinates",
                )
                coordinates[coord_index].extend(array)
            if has_iblank:
                _, index = _take_floats(
                    tokens,
                    index,
                    plane_size,
                    path=path,
                    label=f"K={k} IBLANK array",
                )
    else:
        for coord_index, label in enumerate(labels):
            array, index = _take_floats(
                tokens, index, n, path=path, label=f"{label} coordinates"
            )
            coordinates[coord_index] = array
        if has_iblank:
            _, index = _take_floats(
                tokens, index, n, path=path, label="IBLANK array"
            )

    if index != len(tokens):
        raise Plot3DError(
            f"{path}: {len(tokens) - index} unexpected trailing values for a "
            f"single-grid {dimension}D {organization} layout"
        )

    return [
        GridBlock(
            ni=ni,
            nj=nj,
            nk=nk,
            coordinates=tuple(coordinates),
            source=path,
            block_index=1,
            input_dimension=dimension,
            layout="single",
            organization=organization if dimension == 3 else "whole",
        )
    ]


def _parse_grid_multi(
    tokens: Sequence[str],
    *,
    path: Path,
    dimension: int,
    organization: str,
    has_iblank: bool,
) -> list[GridBlock]:
    nblocks = _as_positive_int(tokens[0], path=path, label="number of grids")
    dims_per_block = 2 if dimension == 2 else 3
    header_end = 1 + dims_per_block * nblocks
    if len(tokens) < header_end:
        raise Plot3DError(
            f"{path}: incomplete multi-grid {dimension}D dimension header"
        )

    dimensions: list[tuple[int, int, int]] = []
    index = 1
    for block in range(1, nblocks + 1):
        ni = _as_positive_int(tokens[index], path=path, label=f"block {block} I")
        nj = _as_positive_int(
            tokens[index + 1], path=path, label=f"block {block} J"
        )
        if dimension == 3:
            nk = _as_positive_int(
                tokens[index + 2], path=path, label=f"block {block} K"
            )
        else:
            nk = 1
        dimensions.append((ni, nj, nk))
        index += dims_per_block

    blocks: list[GridBlock] = []
    labels = ("X", "Y") if dimension == 2 else ("X", "Y", "Z")
    for block, (ni, nj, nk) in enumerate(dimensions, start=1):
        plane_size = ni * nj
        n = plane_size * nk
        coordinates: list[list[float]] = [[] for _ in labels]

        if dimension == 3 and organization == "planes":
            for k in range(1, nk + 1):
                for coord_index, label in enumerate(labels):
                    array, index = _take_floats(
                        tokens,
                        index,
                        plane_size,
                        path=path,
                        label=f"block {block}, K={k}, {label} coordinates",
                    )
                    coordinates[coord_index].extend(array)
                if has_iblank:
                    _, index = _take_floats(
                        tokens,
                        index,
                        plane_size,
                        path=path,
                        label=f"block {block}, K={k}, IBLANK array",
                    )
        else:
            for coord_index, label in enumerate(labels):
                array, index = _take_floats(
                    tokens,
                    index,
                    n,
                    path=path,
                    label=f"block {block} {label} coordinates",
                )
                coordinates[coord_index] = array
            if has_iblank:
                _, index = _take_floats(
                    tokens,
                    index,
                    n,
                    path=path,
                    label=f"block {block} IBLANK array",
                )

        blocks.append(
            GridBlock(
                ni=ni,
                nj=nj,
                nk=nk,
                coordinates=tuple(coordinates),
                source=path,
                block_index=block,
                input_dimension=dimension,
                layout="multi",
                organization=organization if dimension == 3 else "whole",
            )
        )

    if index != len(tokens):
        raise Plot3DError(
            f"{path}: {len(tokens) - index} unexpected trailing values for a "
            f"multi-grid {dimension}D {organization} layout"
        )
    return blocks


def read_grid(
    path: Path,
    *,
    layout: str,
    dimension: str,
    organization: str,
    has_iblank: bool,
) -> list[GridBlock]:
    tokens = _read_tokens(path)
    layouts = ("single", "multi") if layout == "auto" else (layout,)
    dimensions = (2, 3) if dimension == "auto" else (int(dimension[0]),)

    attempts: list[tuple[str, int, list[GridBlock]]] = []
    errors: list[str] = []
    for candidate_layout in layouts:
        for candidate_dimension in dimensions:
            try:
                result = (
                    _parse_grid_single(
                        tokens,
                        path=path,
                        dimension=candidate_dimension,
                        organization=organization,
                        has_iblank=has_iblank,
                    )
                    if candidate_layout == "single"
                    else _parse_grid_multi(
                        tokens,
                        path=path,
                        dimension=candidate_dimension,
                        organization=organization,
                        has_iblank=has_iblank,
                    )
                )
                attempts.append((candidate_layout, candidate_dimension, result))
            except Plot3DError as exc:
                errors.append(
                    f"{candidate_layout}/{candidate_dimension}D/{organization}: {exc}"
                )

    if len(attempts) == 1:
        return attempts[0][2]
    if len(attempts) > 1:
        matches = ", ".join(
            f"{candidate_layout}/{candidate_dimension}D"
            for candidate_layout, candidate_dimension, _ in attempts
        )
        raise Plot3DError(
            f"{path}: layout is ambiguous ({matches}). Specify --input-layout "
            "and/or --input-dimension explicitly."
        )
    raise Plot3DError(
        f"{path}: could not parse a supported formatted PLOT3D grid layout.\n  "
        + "\n  ".join(errors)
    )


def _parse_function_single(
    tokens: Sequence[str],
    *,
    path: Path,
    dimension: int,
    organization: str,
) -> list[FunctionBlock]:
    header_count = 3 if dimension == 2 else 4
    if len(tokens) < header_count:
        raise Plot3DError(
            f"{path}: missing {dimension}D function dimensions or NVAR"
        )

    ni = _as_positive_int(tokens[0], path=path, label="I dimension")
    nj = _as_positive_int(tokens[1], path=path, label="J dimension")
    if dimension == 3:
        nk = _as_positive_int(tokens[2], path=path, label="K dimension")
        nvar_index = 3
    else:
        nk = 1
        nvar_index = 2
    nvar = _as_positive_int(
        tokens[nvar_index], path=path, label="number of variables"
    )

    plane_size = ni * nj
    n = plane_size * nk
    index = header_count
    values: list[list[float]] = [[] for _ in range(nvar)]

    if dimension == 3 and organization == "planes":
        for k in range(1, nk + 1):
            for var_index in range(nvar):
                array, index = _take_floats(
                    tokens,
                    index,
                    plane_size,
                    path=path,
                    label=f"K={k}, function variable {var_index + 1}",
                )
                values[var_index].extend(array)
    else:
        for var_index in range(nvar):
            array, index = _take_floats(
                tokens,
                index,
                n,
                path=path,
                label=f"function variable {var_index + 1}",
            )
            values[var_index] = array

    if index != len(tokens):
        raise Plot3DError(
            f"{path}: {len(tokens) - index} unexpected trailing values for a "
            f"single-grid {dimension}D {organization} function layout"
        )

    return [
        FunctionBlock(
            ni=ni,
            nj=nj,
            nk=nk,
            nvar=nvar,
            values=values,
            source=path,
            block_index=1,
            input_dimension=dimension,
            layout="single",
            organization=organization if dimension == 3 else "whole",
        )
    ]


def _parse_function_multi(
    tokens: Sequence[str],
    *,
    path: Path,
    dimension: int,
    organization: str,
) -> list[FunctionBlock]:
    nblocks = _as_positive_int(tokens[0], path=path, label="number of grids")
    header_values_per_block = 3 if dimension == 2 else 4
    header_end = 1 + header_values_per_block * nblocks
    if len(tokens) < header_end:
        raise Plot3DError(
            f"{path}: incomplete multi-grid {dimension}D function header"
        )

    headers: list[tuple[int, int, int, int]] = []
    index = 1
    for block in range(1, nblocks + 1):
        ni = _as_positive_int(tokens[index], path=path, label=f"block {block} I")
        nj = _as_positive_int(
            tokens[index + 1], path=path, label=f"block {block} J"
        )
        if dimension == 3:
            nk = _as_positive_int(
                tokens[index + 2], path=path, label=f"block {block} K"
            )
            nvar_offset = 3
        else:
            nk = 1
            nvar_offset = 2
        nvar = _as_positive_int(
            tokens[index + nvar_offset],
            path=path,
            label=f"block {block} NVAR",
        )
        headers.append((ni, nj, nk, nvar))
        index += header_values_per_block

    blocks: list[FunctionBlock] = []
    for block, (ni, nj, nk, nvar) in enumerate(headers, start=1):
        plane_size = ni * nj
        n = plane_size * nk
        values: list[list[float]] = [[] for _ in range(nvar)]

        if dimension == 3 and organization == "planes":
            for k in range(1, nk + 1):
                for var_index in range(nvar):
                    array, index = _take_floats(
                        tokens,
                        index,
                        plane_size,
                        path=path,
                        label=(
                            f"block {block}, K={k}, function variable "
                            f"{var_index + 1}"
                        ),
                    )
                    values[var_index].extend(array)
        else:
            for var_index in range(nvar):
                array, index = _take_floats(
                    tokens,
                    index,
                    n,
                    path=path,
                    label=f"block {block}, function variable {var_index + 1}",
                )
                values[var_index] = array

        blocks.append(
            FunctionBlock(
                ni=ni,
                nj=nj,
                nk=nk,
                nvar=nvar,
                values=values,
                source=path,
                block_index=block,
                input_dimension=dimension,
                layout="multi",
                organization=organization if dimension == 3 else "whole",
            )
        )

    if index != len(tokens):
        raise Plot3DError(
            f"{path}: {len(tokens) - index} unexpected trailing values for a "
            f"multi-grid {dimension}D {organization} function layout"
        )
    return blocks


def read_function(
    path: Path,
    *,
    layout: str,
    dimension: str,
    organization: str,
) -> list[FunctionBlock]:
    tokens = _read_tokens(path)
    layouts = ("single", "multi") if layout == "auto" else (layout,)
    dimensions = (2, 3) if dimension == "auto" else (int(dimension[0]),)

    attempts: list[tuple[str, int, list[FunctionBlock]]] = []
    errors: list[str] = []
    for candidate_layout in layouts:
        for candidate_dimension in dimensions:
            try:
                result = (
                    _parse_function_single(
                        tokens,
                        path=path,
                        dimension=candidate_dimension,
                        organization=organization,
                    )
                    if candidate_layout == "single"
                    else _parse_function_multi(
                        tokens,
                        path=path,
                        dimension=candidate_dimension,
                        organization=organization,
                    )
                )
                attempts.append((candidate_layout, candidate_dimension, result))
            except Plot3DError as exc:
                errors.append(
                    f"{candidate_layout}/{candidate_dimension}D/{organization}: {exc}"
                )

    if len(attempts) == 1:
        return attempts[0][2]
    if len(attempts) > 1:
        matches = ", ".join(
            f"{candidate_layout}/{candidate_dimension}D"
            for candidate_layout, candidate_dimension, _ in attempts
        )
        raise Plot3DError(
            f"{path}: function layout is ambiguous ({matches}). Specify "
            "--input-layout and/or --input-dimension explicitly."
        )
    raise Plot3DError(
        f"{path}: could not parse a supported formatted PLOT3D function layout.\n  "
        + "\n  ".join(errors)
    )


def _reduce_array(
    values: Sequence[float],
    *,
    plane_size: int,
    nk: int,
    source_k_index: int | None,
    source_k_average: bool,
    path: Path,
    label: str,
) -> tuple[list[float], str]:
    if nk == 1:
        return list(values), "K=1"

    if source_k_average:
        reduced = [0.0] * plane_size
        for k in range(nk):
            start = k * plane_size
            for index, value in enumerate(values[start : start + plane_size]):
                reduced[index] += value
        return [value / nk for value in reduced], f"mean(K=1..{nk})"

    if source_k_index is None:
        raise Plot3DError(
            f"{path}: {label} has K={nk}. Select one source plane with "
            "--source-k-index N, or use --source-k-average."
        )
    if not 1 <= source_k_index <= nk:
        raise Plot3DError(
            f"{path}: --source-k-index={source_k_index} is outside 1..{nk}"
        )

    start = (source_k_index - 1) * plane_size
    return (
        list(values[start : start + plane_size]),
        f"K={source_k_index} of {nk}",
    )


def reduce_grid_block(
    block: GridBlock,
    *,
    plane: str,
    source_k_index: int | None,
    source_k_average: bool,
) -> GridCut:
    if block.input_dimension == 2:
        first_full, second_full = block.coordinates
    else:
        x_full, y_full, z_full = block.coordinates
        if plane == "xy":
            first_full, second_full = x_full, y_full
        elif plane == "xz":
            first_full, second_full = x_full, z_full
        elif plane == "yz":
            first_full, second_full = y_full, z_full
        else:
            raise AssertionError(f"Unsupported plane: {plane}")

    c1, reduction = _reduce_array(
        first_full,
        plane_size=block.plane_size,
        nk=block.nk,
        source_k_index=source_k_index,
        source_k_average=source_k_average,
        path=block.source,
        label=f"grid block {block.block_index}",
    )
    c2, reduction2 = _reduce_array(
        second_full,
        plane_size=block.plane_size,
        nk=block.nk,
        source_k_index=source_k_index,
        source_k_average=source_k_average,
        path=block.source,
        label=f"grid block {block.block_index}",
    )
    if reduction != reduction2:
        raise AssertionError("Coordinate reductions do not match")

    return GridCut(
        ni=block.ni,
        nj=block.nj,
        c1=c1,
        c2=c2,
        source=block.source,
        block_index=block.block_index,
        source_nk=block.nk,
        reduction=reduction,
    )


def reduce_function_block(
    block: FunctionBlock,
    *,
    source_k_index: int | None,
    source_k_average: bool,
) -> FunctionCut:
    reduced_values: list[list[float]] = []
    reduction = ""
    for var_index, variable in enumerate(block.values, start=1):
        reduced, current_reduction = _reduce_array(
            variable,
            plane_size=block.plane_size,
            nk=block.nk,
            source_k_index=source_k_index,
            source_k_average=source_k_average,
            path=block.source,
            label=f"function block {block.block_index}, variable {var_index}",
        )
        if reduction and reduction != current_reduction:
            raise AssertionError("Function reductions do not match")
        reduction = current_reduction
        reduced_values.append(reduced)

    return FunctionCut(
        ni=block.ni,
        nj=block.nj,
        nvar=block.nvar,
        values=reduced_values,
        source=block.source,
        block_index=block.block_index,
        source_nk=block.nk,
        reduction=reduction,
    )


def _write_values(handle, values: Iterable[float], values_per_line: int) -> None:
    count = 0
    for value in values:
        handle.write(f" {value:.16e}")
        count += 1
        if count % values_per_line == 0:
            handle.write("\n")
    if count % values_per_line:
        handle.write("\n")


def _check_output_path(path: Path, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise Plot3DError(
            f"Output file already exists: {path}. Use --overwrite to replace it."
        )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise Plot3DError(f"Cannot create output directory for {path}: {exc}") from exc


def _resolve_positions(args: argparse.Namespace, count: int) -> list[float]:
    modes = sum(
        (
            args.positions is not None,
            args.positions_file is not None,
            args.position_start is not None or args.position_step is not None,
        )
    )
    if modes != 1:
        raise Plot3DError(
            "Specify exactly one position mode: --positions, --positions-file, "
            "or both --position-start and --position-step."
        )

    if args.positions is not None:
        positions = list(args.positions)
    elif args.positions_file is not None:
        try:
            raw = args.positions_file.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise Plot3DError(f"Cannot read positions file: {exc}") from exc
        try:
            positions = [
                float(token.replace("D", "E").replace("d", "e"))
                for token in raw.replace(",", " ").split()
            ]
        except ValueError as exc:
            raise Plot3DError(
                f"{args.positions_file}: positions file contains a nonnumeric value"
            ) from exc
    else:
        if args.position_start is None or args.position_step is None:
            raise Plot3DError(
                "--position-start and --position-step must be supplied together"
            )
        positions = [
            args.position_start + index * args.position_step for index in range(count)
        ]

    if len(positions) != count:
        raise Plot3DError(
            f"Expected {count} slice positions, but received {len(positions)}"
        )
    if any(not math.isfinite(value) for value in positions):
        raise Plot3DError("All slice positions must be finite numbers")
    if len(set(positions)) != len(positions):
        raise Plot3DError("Slice positions must be unique")

    if len(positions) >= 2:
        increasing = all(a < b for a, b in zip(positions, positions[1:]))
        decreasing = all(a > b for a, b in zip(positions, positions[1:]))
        if not (increasing or decreasing):
            raise Plot3DError(
                "Slice positions must be strictly monotonic in input order"
            )
    return positions


def _global_coordinates(
    grid: GridCut, position: float, plane: str
) -> tuple[list[float], list[float], list[float]]:
    constant = [position] * grid.size
    if plane == "xy":
        return grid.c1, grid.c2, constant
    if plane == "xz":
        return grid.c1, constant, grid.c2
    if plane == "yz":
        return constant, grid.c1, grid.c2
    raise AssertionError(f"Unsupported plane mapping: {plane}")


def _validate_blocks(
    grids: Sequence[GridCut], functions: Sequence[FunctionCut] | None
) -> tuple[int, int, int]:
    if not grids:
        raise Plot3DError("No grid cuts were found")

    ni, nj = grids[0].ni, grids[0].nj
    for index, grid in enumerate(grids, start=1):
        if (grid.ni, grid.nj) != (ni, nj):
            raise Plot3DError(
                f"Grid cut {index} ({grid.source}, block {grid.block_index}) has "
                f"dimensions {grid.ni}x{grid.nj}; expected {ni}x{nj}. "
                "Interpolate all cuts to a common grid before stacking."
            )

    if functions is None:
        return ni, nj, 0
    if len(functions) != len(grids):
        raise Plot3DError(
            f"Found {len(grids)} grid cuts but {len(functions)} function cuts"
        )

    nvar = functions[0].nvar
    for index, (grid, function) in enumerate(zip(grids, functions), start=1):
        if (function.ni, function.nj) != (grid.ni, grid.nj):
            raise Plot3DError(
                f"Cut {index}: function dimensions {function.ni}x{function.nj} "
                f"do not match grid dimensions {grid.ni}x{grid.nj}"
            )
        if function.nvar != nvar:
            raise Plot3DError(
                f"Cut {index}: function file has {function.nvar} variables; "
                f"expected {nvar}"
            )
        if function.source_nk != grid.source_nk:
            raise Plot3DError(
                f"Cut {index}: grid K={grid.source_nk}, but function "
                f"K={function.source_nk}"
            )
    return ni, nj, nvar


def _warn_nonfinite(
    grids: Sequence[GridCut], functions: Sequence[FunctionCut] | None
) -> None:
    coordinate_count = sum(
        not math.isfinite(value)
        for grid in grids
        for value in (*grid.c1, *grid.c2)
    )
    function_count = 0
    if functions is not None:
        function_count = sum(
            not math.isfinite(value)
            for block in functions
            for variable in block.values
            for value in variable
        )
    if coordinate_count:
        print(
            f"WARNING: preserving {coordinate_count} non-finite coordinate values.",
            file=sys.stderr,
        )
    if function_count:
        print(
            f"WARNING: preserving {function_count} non-finite function values.",
            file=sys.stderr,
        )


def convert(args: argparse.Namespace) -> None:
    grid_blocks: list[GridBlock] = []
    for path in args.grid_files:
        grid_blocks.extend(
            read_grid(
                path,
                layout=args.input_layout,
                dimension=args.input_dimension,
                organization=args.input_organization,
                has_iblank=args.input_iblank,
            )
        )

    function_blocks: list[FunctionBlock] | None = None
    if args.function_files:
        function_blocks = []
        for path in args.function_files:
            function_blocks.extend(
                read_function(
                    path,
                    layout=args.input_layout,
                    dimension=args.input_dimension,
                    organization=args.input_organization,
                )
            )

    grid_cuts = [
        reduce_grid_block(
            block,
            plane=args.plane,
            source_k_index=args.source_k_index,
            source_k_average=args.source_k_average,
        )
        for block in grid_blocks
    ]
    function_cuts = (
        [
            reduce_function_block(
                block,
                source_k_index=args.source_k_index,
                source_k_average=args.source_k_average,
            )
            for block in function_blocks
        ]
        if function_blocks is not None
        else None
    )

    ni, nj, nvar = _validate_blocks(grid_cuts, function_cuts)
    positions = _resolve_positions(args, len(grid_cuts))
    nk = len(grid_cuts)
    _warn_nonfinite(grid_cuts, function_cuts)

    if args.output_function is not None and function_cuts is None:
        raise Plot3DError(
            "--output-function was supplied, but no --function-files were supplied"
        )
    if function_cuts is not None and args.output_function is None:
        raise Plot3DError(
            "Function input was supplied; specify --output-function for the 3D file"
        )

    _check_output_path(args.output_grid, overwrite=args.overwrite)
    if args.output_function is not None:
        _check_output_path(args.output_function, overwrite=args.overwrite)

    all_x: list[float] = []
    all_y: list[float] = []
    all_z: list[float] = []
    for grid, position in zip(grid_cuts, positions):
        gx, gy, gz = _global_coordinates(grid, position, args.plane)
        all_x.extend(gx)
        all_y.extend(gy)
        all_z.extend(gz)

    try:
        with args.output_grid.open("w", encoding="ascii", newline="\n") as handle:
            handle.write(f"{ni} {nj} {nk}\n")
            _write_values(handle, all_x, args.values_per_line)
            _write_values(handle, all_y, args.values_per_line)
            _write_values(handle, all_z, args.values_per_line)
    except OSError as exc:
        raise Plot3DError(f"Cannot write {args.output_grid}: {exc}") from exc

    if function_cuts is not None and args.output_function is not None:
        try:
            with args.output_function.open(
                "w", encoding="ascii", newline="\n"
            ) as handle:
                handle.write(f"{ni} {nj} {nk} {nvar}\n")
                for var_index in range(nvar):
                    stacked: list[float] = []
                    for block in function_cuts:
                        stacked.extend(block.values[var_index])
                    _write_values(handle, stacked, args.values_per_line)
        except OSError as exc:
            raise Plot3DError(f"Cannot write {args.output_function}: {exc}") from exc

    if args.name_file is not None:
        output_name_file = args.output_name_file
        if output_name_file is None:
            base = (
                args.output_function
                if args.output_function is not None
                else args.output_grid
            )
            output_name_file = base.with_suffix(".nam")
        _check_output_path(output_name_file, overwrite=args.overwrite)
        try:
            shutil.copyfile(args.name_file, output_name_file)
        except OSError as exc:
            raise Plot3DError(
                f"Cannot copy name file {args.name_file} to {output_name_file}: {exc}"
            ) from exc
        print(f"Copied name file: {output_name_file}")

    axis = {"xy": "Z", "xz": "Y", "yz": "X"}[args.plane]
    unique_formats = sorted(
        {
            f"{block.layout}/{block.input_dimension}D/{block.organization}"
            for block in grid_blocks
        }
    )
    print("Conversion completed successfully.")
    print(f"  Input grid layout(s): {', '.join(unique_formats)}")
    print(f"  Source reduction: {grid_cuts[0].reduction}")
    print(f"  Output dimensions: I={ni}, J={nj}, K={nk}")
    print(f"  Stacking coordinate: {axis}")
    print(f"  Positions: {positions}")
    print(f"  Variables: {nvar}")
    print(f"  Grid output: {args.output_grid}")
    if args.output_function is not None:
        print(f"  Function output: {args.output_function}")
    print("FieldView reader settings:")
    print("  format=formatted, coords=3d, multi_grid=off, iblanks=off")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Stack formatted-ASCII PLOT3D cuts, including K=2 thin slabs, "
            "into one single-grid 3D PLOT3D volume."
        )
    )
    parser.add_argument(
        "--grid-files",
        type=Path,
        nargs="+",
        required=True,
        help="Formatted PLOT3D grid files in physical cut order.",
    )
    parser.add_argument(
        "--function-files",
        type=Path,
        nargs="+",
        help="Matching formatted PLOT3D function files in the same order.",
    )
    parser.add_argument(
        "--input-layout",
        choices=("auto", "single", "multi"),
        default="auto",
        help=(
            "PLOT3D container layout. 'multi' means a leading number-of-grids "
            "value, even when it is 1. Default: auto."
        ),
    )
    parser.add_argument(
        "--input-dimension",
        choices=("auto", "2d", "3d"),
        default="auto",
        help="Input PLOT3D coordinate dimensionality. Default: auto.",
    )
    parser.add_argument(
        "--input-organization",
        choices=("whole", "planes"),
        default="whole",
        help=(
            "3D PLOT3D data organization. Use the same setting shown in "
            "Tecplot's PLOT3D File Structure page. Default: whole."
        ),
    )
    parser.add_argument(
        "--input-iblank",
        action="store_true",
        help="Read and discard an IBLANK array after each grid block.",
    )
    parser.add_argument(
        "--plane",
        choices=("xy", "xz", "yz"),
        default="xy",
        help=(
            "Physical plane of each cut. xy stacks in Z; xz stacks in Y; "
            "yz stacks in X. Default: xy."
        ),
    )

    reduction_group = parser.add_mutually_exclusive_group()
    reduction_group.add_argument(
        "--source-k-index",
        type=int,
        help=(
            "For a source block with K>1, extract this 1-based K plane. "
            "Example: --source-k-index 1."
        ),
    )
    reduction_group.add_argument(
        "--source-k-average",
        action="store_true",
        help="For a source block with K>1, average all K planes point-by-point.",
    )

    position_group = parser.add_argument_group("cut positions")
    position_group.add_argument(
        "--positions",
        type=float,
        nargs="+",
        help="Physical stacking position of every cut/block, in input order.",
    )
    position_group.add_argument(
        "--positions-file",
        type=Path,
        help="Text file containing whitespace/comma-separated positions.",
    )
    position_group.add_argument(
        "--position-start",
        type=float,
        help="First position for uniformly spaced cuts; use with --position-step.",
    )
    position_group.add_argument(
        "--position-step",
        type=float,
        help="Uniform spacing between cuts; use with --position-start.",
    )

    parser.add_argument(
        "--output-grid",
        type=Path,
        required=True,
        help="Output single-grid 3D formatted PLOT3D grid file.",
    )
    parser.add_argument(
        "--output-function",
        type=Path,
        help="Output matching 3D formatted PLOT3D function file.",
    )
    parser.add_argument(
        "--name-file",
        type=Path,
        help="Optional existing PLOT3D function-name file to copy unchanged.",
    )
    parser.add_argument(
        "--output-name-file",
        type=Path,
        help="Destination for --name-file; default: output base name with .nam.",
    )
    parser.add_argument(
        "--values-per-line",
        type=int,
        default=5,
        help="Number of ASCII data values per output line. Default: 5.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of existing output files.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.values_per_line <= 0:
        parser.error("--values-per-line must be positive")
    if args.source_k_index is not None and args.source_k_index <= 0:
        parser.error("--source-k-index must be a positive 1-based index")

    try:
        convert(args)
    except Plot3DError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

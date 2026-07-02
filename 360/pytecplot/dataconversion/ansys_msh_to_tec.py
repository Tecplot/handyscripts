#!/usr/bin/env python3
"""Convert Fluent/ANSYS .msh files to Tecplot .szplt.

The script accepts one or more input paths and writes
"inputfile_tec.szplt" beside each input file.

Usage:
"python ansys_msh_to_tec.py path/to/inputfile.msh
"""

from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import dataclass
import math
from pathlib import Path
import re
import sys
import tecplot as tp
from typing import Dict, List, Tuple
from tecplot.constant import FECellShape, PlotType, ZoneType

NODES_SECTION = 10
CELLS_SECTION = 12
FACES_SECTION = 13
FLOAT32_MAX = 3.4028235e38
FIXED_FACE_NODES = {
    2: 2,
    3: 3,
    4: 4,
}


@dataclass
class FluentMesh:
    dimension: int = 3
    nodes: Dict[int, Tuple[float, float, float]] | None = None
    faces: List[Tuple[Tuple[int, ...], int, int]] | None = None
    max_cell_id: int = 0

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = {}
        if self.faces is None:
            self.faces = []


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Fluent .msh files. Defaults to all .msh files in the current directory.",
    )
    parser.add_argument(
        "-c",
        action="store_true",
        help="Connect to a running Tecplot 360 session.",
    )
    return parser.parse_args(argv)


def iter_top_level_sections(path, chunk_size=1024 * 1024):
    depth = 0
    buf: List[str] = []
    in_section = False

    with path.open("r", encoding="latin-1", errors="replace") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break

            i = 0
            n = len(chunk)
            while i < n:
                ch = chunk[i]

                if ch == ";":
                    j = chunk.find("\n", i)
                    if j == -1:
                        break
                    if in_section:
                        buf.append(" ")
                    i = j + 1
                    continue

                if ch == "(":
                    depth += 1
                    in_section = True
                    buf.append(ch)
                elif ch == ")":
                    if in_section:
                        buf.append(ch)
                    depth -= 1
                    if depth == 0 and in_section:
                        yield "".join(buf)
                        buf.clear()
                        in_section = False
                    elif depth < 0:
                        raise ValueError(f"Unbalanced ')' while reading {path}")
                elif in_section:
                    buf.append(ch)

                i += 1

    if depth != 0:
        raise ValueError(f"Unbalanced parentheses in {path}")


def _section_header_and_body(section):
    match = re.match(r"\s*\(\s*([0-9A-Fa-f]+)", section)
    if not match:
        return None, [], None

    section_id = int(match.group(1), 10)
    header_start = section.find("(", match.end())
    if header_start < 0:
        return section_id, [], None

    depth = 0
    header_end = None
    for idx in range(header_start, len(section)):
        if section[idx] == "(":
            depth += 1
        elif section[idx] == ")":
            depth -= 1
            if depth == 0:
                header_end = idx + 1
                break

    if header_end is None:
        return section_id, [], None

    header = re.findall(r"[^\s()]+", section[header_start + 1 : header_end - 1])

    idx = header_end
    while idx < len(section) and section[idx].isspace():
        idx += 1
    if idx >= len(section) or section[idx] != "(":
        return section_id, header, None

    depth = 0
    for end_idx in range(idx, len(section)):
        if section[end_idx] == "(":
            depth += 1
        elif section[end_idx] == ")":
            depth -= 1
            if depth == 0:
                return section_id, header, section[idx + 1 : end_idx]
    return section_id, header, None


def _parse_nodes(section, mesh):
    _, header, body = _section_header_and_body(section)
    if len(header) >= 5 and header[0] == "0":
        try:
            mesh.dimension = int(header[4], 16)
        except Exception:
            pass
        return

    if len(header) < 5:
        return

    first = int(header[1], 16)
    last = int(header[2], 16)
    dim = int(header[4], 16)
    mesh.dimension = max(mesh.dimension, dim)

    if body is None:
        return

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    expected = last - first + 1
    if len(lines) != expected:
        print(
            f"Warning: node section says {expected:,} nodes but parsed {len(lines):,}",
            file=sys.stderr,
        )

    def parse_coord(token):
        token = token.replace("D", "E").replace("d", "e")
        return float(token)

    for offset, line in enumerate(lines):
        values = line.split()
        if len(values) < dim:
            raise ValueError(
                f"Node section line {offset + 1} has {len(values)} values; expected {dim}"
            )
        x = parse_coord(values[0])
        y = parse_coord(values[1]) if dim >= 2 else 0.0
        z = parse_coord(values[2]) if dim >= 3 else 0.0
        mesh.nodes[first + offset] = (x, y, z)


def _parse_cells(section, mesh):
    _, header, _ = _section_header_and_body(section)
    if len(header) < 3:
        return
    try:
        last = int(header[2], 16)
    except Exception:
        return
    mesh.max_cell_id = max(mesh.max_cell_id, last)


def _parse_faces(section, mesh):
    _, header, body = _section_header_and_body(section)
    if len(header) >= 5 and header[0] == "0":
        return
    if len(header) < 5:
        return

    first = int(header[1], 16)
    last = int(header[2], 16)
    face_type = int(header[4], 16)
    nfaces = last - first + 1

    if body is None:
        return

    tokens = re.findall(r"[^\s()]+", body)
    idx = 0

    for _ in range(nfaces):
        if face_type in FIXED_FACE_NODES:
            node_count = FIXED_FACE_NODES[face_type]
        else:
            if idx >= len(tokens):
                raise ValueError("Unexpected end of face data while reading node count")
            node_count = int(tokens[idx], 16)
            idx += 1

        if idx + node_count + 2 > len(tokens):
            raise ValueError("Unexpected end of face data while reading nodes/cells")

        nodes = tuple(int(token, 16) for token in tokens[idx : idx + node_count])
        idx += node_count
        left_cell = int(tokens[idx], 16)
        right_cell = int(tokens[idx + 1], 16)
        idx += 2

        mesh.max_cell_id = max(mesh.max_cell_id, left_cell, right_cell)
        mesh.faces.append((nodes, left_cell, right_cell))


def parse_fluent_msh(path):
    mesh = FluentMesh()
    section_count = 0

    for section in iter_top_level_sections(path):
        section_count += 1
        section_id, _, _ = _section_header_and_body(section)
        if section_id == NODES_SECTION:
            _parse_nodes(section, mesh)
        elif section_id == CELLS_SECTION:
            _parse_cells(section, mesh)
        elif section_id == FACES_SECTION:
            _parse_faces(section, mesh)

        if section_count % 100 == 0:
            print(
                f"Parsed {section_count} sections: "
                f"{len(mesh.nodes):,} nodes, {len(mesh.faces):,} faces, "
                f"max cell {mesh.max_cell_id:,}",
                flush=True,
            )

    if not mesh.nodes:
        raise ValueError("No nodes found. This script supports ASCII Fluent .msh files.")
    if not mesh.faces:
        raise ValueError("No faces found. This script supports ASCII Fluent .msh files.")

    return mesh

def create_tecplot_dataset(mesh, title):

    referenced = {node_id for face_nodes, _, _ in mesh.faces for node_id in face_nodes}
    if referenced:
        missing = sorted(node_id for node_id in referenced if node_id not in mesh.nodes)
        if missing:
            raise ValueError(
                f"Faces reference {len(missing):,} missing node ids. First few: {missing[:10]}"
            )
        node_ids = sorted(referenced)
    else:
        node_ids = sorted(mesh.nodes)
    node_index = {node_id: idx for idx, node_id in enumerate(node_ids)}
    coords = [mesh.nodes[node_id] for node_id in node_ids]

    for node_id, coord in zip(node_ids, coords):
        for axis, value in zip(("X", "Y", "Z"), coord):
            if not math.isfinite(value):
                raise ValueError(f"Node {node_id} has non-finite {axis} coordinate: {value}")
            if abs(value) > FLOAT32_MAX:
                raise ValueError(
                    f"Node {node_id} has {axis}={value}, which exceeds float32 range"
                )

    dropped_nodes = len(mesh.nodes) - len(node_ids)
    if dropped_nodes:
        invalid_dropped = sum(
            1
            for node_id, coord in mesh.nodes.items()
            if node_id not in node_index
            and any((not math.isfinite(value)) or abs(value) > FLOAT32_MAX for value in coord)
        )
        message = (
            f"Using {len(node_ids):,} face-referenced nodes out of {len(mesh.nodes):,}; "
            f"dropped {dropped_nodes:,} unreferenced nodes"
        )
        if invalid_dropped:
            message += f" ({invalid_dropped:,} had invalid/overflowing coordinates)"
        print(message)

    tp.new_layout()
    frame = tp.active_frame()
    frame.plot(PlotType.Sketch).activate()

    dataset = frame.create_dataset(title, ["X", "Y", "Z"])

    if mesh.max_cell_id > 0 and any(left > 0 or right > 0 for _, left, right in mesh.faces):
        zone_type = ZoneType.FEPolygon if mesh.dimension <= 2 else ZoneType.FEPolyhedron

        faces = []
        left_cells = []
        right_cells = []

        for face_nodes, left_cell, right_cell in mesh.faces:
            faces.append(tuple(node_index[node_id] for node_id in face_nodes))
            left_cells.append(left_cell - 1 if left_cell > 0 else -1)
            right_cells.append(right_cell - 1 if right_cell > 0 else -1)

        zone = dataset.add_poly_zone(
            zone_type,
            name=title,
            num_points=len(node_ids),
            num_elements=mesh.max_cell_id,
            num_faces=len(faces),
        )
        zone.values("X")[:] = [coord[0] for coord in coords]
        zone.values("Y")[:] = [coord[1] for coord in coords]
        zone.values("Z")[:] = [coord[2] for coord in coords]
        zone.facemap.set_mapping(faces, (left_cells, right_cells))
        return dataset

    counts = Counter(len(face_nodes) for face_nodes, _, _ in mesh.faces)
    unsupported = sorted(count for count in counts if count not in (3, 4))
    if unsupported:
        raise ValueError(
            "Face-only meshes are currently supported only for triangle/quad faces. "
            f"Unsupported face sizes: {unsupported}"
        )

    sections = []
    if counts.get(3):
        sections.append((counts[3], FECellShape.Triangle))
    if counts.get(4):
        sections.append((counts[4], FECellShape.Quadrilateral))

    zone = dataset.add_fe_mixed_zone(title, len(node_ids), sections)
    zone.values("X")[:] = [coord[0] for coord in coords]
    zone.values("Y")[:] = [coord[1] for coord in coords]
    zone.values("Z")[:] = [coord[2] for coord in coords]

    triangles = []
    quads = []
    for face_nodes, _, _ in mesh.faces:
        conn = tuple(node_index[node_id] for node_id in face_nodes)
        if len(conn) == 3:
            triangles.append(conn)
        else:
            quads.append(conn)

    section_index = 0
    if triangles:
        zone.nodemap.section(section_index)[:] = triangles
        section_index += 1
    if quads:
        zone.nodemap.section(section_index)[:] = quads

    return dataset


def main(argv=None):
    args = parse_args(argv)
    failures = 0

    if args.c:
        tp.session.connect()

    input_names = args.inputs or sorted(str(path) for path in Path.cwd().glob("*.msh"))
    if not input_names:
        print("No .msh files found in the current directory.", file=sys.stderr)
        return 1

    for input_name in input_names:
        try:
            input_path = Path(input_name).expanduser()
            if not (input_path.is_file() and input_path.suffix.lower() == ".msh"):
                raise FileNotFoundError(f"Could not find Fluent .msh file: '{input_name}'")
            input_path = input_path.resolve()
            output_path = input_path.with_name(f"{input_path.stem}_tec.szplt")

            print(f"Reading {input_path}")
            mesh = parse_fluent_msh(input_path)
            print(
                f"Parsed mesh: dimension={mesh.dimension}, "
                f"nodes={len(mesh.nodes):,}, faces={len(mesh.faces):,}, cells={mesh.max_cell_id:,}"
            )

            print("Creating Tecplot dataset")
            with tp.session.suspend():
                dataset = create_tecplot_dataset(mesh, input_path.stem)

            print(f"Writing {output_path}")
            tp.data.save_tecplot_szl(str(output_path), dataset=dataset)
        except Exception as exc:
            failures += 1
            print(f"FAILED: {input_name}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

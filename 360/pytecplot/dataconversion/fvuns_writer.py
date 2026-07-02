#!/usr/bin/env python3
"""Export Tecplot data to a combined binary FV-UNS file.

- connected mode: use the dataset currently loaded in a live Tecplot 360 session
- batch mode: load a dataset from an input file through PyTecplot, then export it

Supported:
- 3D unstructured zones only
- classic FE zones: FETetra and FEBrick, including collapsed FEBrick elements
  that represent tets, prisms, and pyramids
- polyhedral zones: FEPolyhedron
- nodal result variables only
- no boundary-face result variables

Unsupported data is skipped or rejected explicitly instead of being written in a
format that is likely invalid.
"""

from __future__ import annotations

import argparse
import fnmatch
import math
import numpy as np
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import tecplot as tp
from tecplot.constant import FECellShape, ValueLocation, ZoneType
from tecplot.data.facemap import Elementmap


FVUNS_VERSION_MAJOR = 3
FVUNS_VERSION_MINOR = 0
FLOAT_FORMAT = ".9g"

FV_MAGIC = 0x00010203
FV_COMBINED_FILE = 3

FV_NODES = 1001
FV_FACES = 1002
FV_ELEMENTS = 1003
FV_VARIABLES = 1004
FV_BNDRY_VARS = 1006
FV_ARB_POLY_FACES = 1007
FV_ARB_POLY_ELEMENTS = 1008
FV_ARB_POLY_BNDRY_VARS = 1009

A_WALL = 0o7
NOT_A_WALL = 0
MAX_NUM_ELEM_FACES = 6
BITS_PER_WALL = 3
ELEM_TYPE_BIT_SHIFT = MAX_NUM_ELEM_FACES * BITS_PER_WALL


CLASSIC_FACE_TEMPLATES = {
    "tet": ((0, 1, 2), (0, 3, 1), (1, 3, 2), (0, 2, 3)),
    "hex": ((0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)),
    "prism": ((0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)),
    "pyramid": ((0, 1, 2, 3), (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0)),
}

FVUNS_ELEMENT_TYPE = {
    "tet": 1,
    "hex": 2,
    "prism": 3,
    "pyramid": 4,
    "polyhedron": 5,
}


@dataclass
class BoundaryType:
    name: str
    wall_flag: int = 0
    surface_results_flag: int = 0
    clockness_flag: int = 1


@dataclass
class BoundaryFace:
    boundary_type_index: int
    nodes: list[int]


@dataclass
class ClassicElement:
    kind: str
    nodes: list[int]


@dataclass
class PolyFaceRecord:
    nodes: list[int]
    hanging_nodes: list[int]


@dataclass
class PolyElement:
    faces: list[PolyFaceRecord]
    num_nodes_including_center_node: int
    center_node_number: int


@dataclass
class ZoneExport:
    name: str
    num_nodes: int
    coordinates: list[tuple[float, float, float]]
    boundary_faces: list[BoundaryFace]
    classic_elements: list[ClassicElement]
    poly_elements: list[PolyElement]
    nodal_results: list[list[float]]


@dataclass
class StandardBoundarySection:
    boundary_type_index: int
    faces: list[list[int]]


@dataclass
class ArbitraryBoundarySection:
    boundary_type_index: int
    faces: list[list[int]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", action="store_true", help="Use connected mode with the currently loaded Tecplot 360 dataset.")
    parser.add_argument("-infile", default=None, help="Input dataset file to load in batch mode.")
    parser.add_argument("-outfile", required=True, help="Output path for the combined binary FV-UNS file.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=7600,
        help="Tecplot PyTecplot connection port. Default: 7600",
    )
    parser.add_argument(
        "-z",
        "--zones",
        nargs="*",
        default=None,
        help="Optional zone selectors. Each selector may be a zero-based index, exact name, or wildcard pattern.",
    )
    parser.add_argument("--xvar", default=None, help="Override the X coordinate variable name.")
    parser.add_argument("--yvar", default=None, help="Override the Y coordinate variable name.")
    parser.add_argument("--zvar", default=None, help="Override the Z coordinate variable name.")
    parser.add_argument("--time", type=float, default=0.0, help="Solution time constant.")
    parser.add_argument("--fsmach", type=float, default=0.0, help="Free-stream Mach constant.")
    parser.add_argument("--alpha", type=float, default=0.0, help="Angle of attack constant.")
    parser.add_argument("--re", type=float, default=0.0, help="Reynolds number constant.")
    args = parser.parse_args()
    if args.c and args.infile:
        parser.error("Use either -c or -infile, not both.")
    if not args.c and not args.infile:
        parser.error("You must provide either -c or -infile.")
    return args


def connect_to_tecplot(port: int) -> None:
    print(f"Connecting to Tecplot 360 on port {port}...")
    try:
        tp.session.connect(port=port)
    except Exception as exc:  # pragma: no cover - depends on live Tecplot session
        raise RuntimeError(
            "Failed to connect to Tecplot 360. Enable 'Accept connections' in Tecplot 360 "
            f"and ensure the session is listening on port {port}."
        ) from exc
    print("Connected to Tecplot 360.")


def active_dataset():
    frame = tp.active_frame()
    if frame is None or frame.dataset is None:
        raise RuntimeError("No active Tecplot frame/dataset is available.")
    return frame.dataset


def load_dataset_from_file(input_path: str):
    path = Path(input_path)
    if not path.exists():
        raise RuntimeError(f"Input file does not exist: {input_path}")

    print(f"Loading dataset from file: {path}")
    lower_name = path.name.lower()
    if lower_name.endswith(".szplt") or lower_name.endswith(".szl"):
        dataset = tp.data.load_tecplot_szl(str(path))
    else:
        dataset = tp.data.load_tecplot(str(path))
    print("Dataset loaded.")
    return dataset


def resolve_variable_name(dataset, explicit_name: str | None, candidates: Sequence[str], axis_label: str) -> str:
    if explicit_name is not None:
        dataset.variable(explicit_name)
        return explicit_name
    lowered = {name.lower(): name for name in dataset.variable_names}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    raise RuntimeError(f"Could not determine the {axis_label} coordinate variable. Use --{axis_label.lower()}var.")


def select_zones(dataset, selectors: Sequence[str] | None):
    all_zones = list(dataset.zones())
    indexed_zones = list(enumerate(all_zones))
    if not selectors:
        return [zone for zone in all_zones if is_supported_export_zone(zone)]

    matched = []
    seen = set()
    for selector in selectors:
        if selector.isdigit():
            zone = dataset.zone(int(selector))
            zone_key = id(zone)
            if zone_key not in seen:
                matched.append(zone)
                seen.add(zone_key)
            continue
        exact = next((zone for _, zone in indexed_zones if zone.name == selector), None)
        if exact is not None:
            zone_key = id(exact)
            if zone_key not in seen:
                matched.append(exact)
                seen.add(zone_key)
            continue
        wildcards = [zone for _, zone in indexed_zones if fnmatch.fnmatch(zone.name, selector)]
        for zone in wildcards:
            zone_key = id(zone)
            if zone_key not in seen:
                matched.append(zone)
                seen.add(zone_key)

    return [zone for zone in matched if is_supported_export_zone(zone)]


def print_zone_inventory(dataset) -> None:
    print("Dataset zone inventory:")
    for zone_index, zone in enumerate(dataset.zones()):
        print(f"  [{zone_index}] name='{zone.name}' type={zone.zone_type} rank={zone.rank}")


def is_supported_volume_zone(zone) -> bool:
    return zone.rank == 3 and zone.zone_type in {ZoneType.FETetra, ZoneType.FEBrick, ZoneType.FEPolyhedron, ZoneType.FEMixed}


def is_supported_surface_zone(zone) -> bool:
    return zone.rank == 2 and zone.zone_type in {ZoneType.FETriangle, ZoneType.FEQuad, ZoneType.FEPolygon, ZoneType.FEMixed}


def is_supported_export_zone(zone) -> bool:
    return is_supported_volume_zone(zone) or is_supported_surface_zone(zone)


def sanitize_boundary_name(raw_name: str, used_names: set[str]) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "_", raw_name).strip() or "Boundary"
    if not cleaned[0].isalpha():
        cleaned = f"B_{cleaned}"
    base = cleaned[:80]
    candidate = base
    suffix = 1
    while candidate.lower() in used_names:
        suffix_text = f"_{suffix}"
        candidate = (base[: 80 - len(suffix_text)] + suffix_text).strip()
        suffix += 1
    used_names.add(candidate.lower())
    return candidate


def format_float(value: float) -> str:
    if not math.isfinite(value):
        raise RuntimeError(f"Encountered a non-finite floating point value: {value!r}")
    return format(float(value), FLOAT_FORMAT)


def orient_face_outward(nodes: Sequence[int], coordinates: Sequence[tuple[float, float, float]], element_nodes: Sequence[int]) -> list[int]:
    face = list(nodes)
    if len(face) < 3:
        return face
    cell_centroid = centroid(coordinates[index] for index in element_nodes)
    face_centroid = centroid(coordinates[index] for index in face)
    normal = polygon_normal([coordinates[index] for index in face])
    direction = (
        face_centroid[0] - cell_centroid[0],
        face_centroid[1] - cell_centroid[1],
        face_centroid[2] - cell_centroid[2],
    )
    if dot(normal, direction) < 0.0:
        face.reverse()
    return face


def centroid(points: Iterable[tuple[float, float, float]]) -> tuple[float, float, float]:
    pts = list(points)
    count = len(pts)
    return (
        sum(point[0] for point in pts) / count,
        sum(point[1] for point in pts) / count,
        sum(point[2] for point in pts) / count,
    )


def polygon_normal(points: Sequence[tuple[float, float, float]]) -> tuple[float, float, float]:
    origin = points[0]
    for i in range(1, len(points) - 1):
        v1 = subtract(points[i], origin)
        v2 = subtract(points[i + 1], origin)
        cross_product = cross(v1, v2)
        if magnitude(cross_product) > 0.0:
            return cross_product
    return (0.0, 0.0, 0.0)


def subtract(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def magnitude(vector: tuple[float, float, float]) -> float:
    return math.sqrt(dot(vector, vector))


def classify_fe_brick_element(nodemap_row: Sequence[int]) -> ClassicElement:
    row = list(nodemap_row)
    if len(row) != 8:
        raise RuntimeError(f"Unsupported FEBrick nodemap width: expected 8, got {len(row)}")

    if row[2] == row[3] and row[4] == row[5] == row[6] == row[7]:
        return ClassicElement(kind="tet", nodes=[row[0], row[1], row[2], row[4]])
    if row[2] == row[3] and row[6] == row[7]:
        return ClassicElement(kind="prism", nodes=[row[0], row[1], row[2], row[4], row[5], row[6]])
    if row[4] == row[5] == row[6] == row[7]:
        return ClassicElement(kind="pyramid", nodes=[row[0], row[1], row[2], row[3], row[4]])
    return ClassicElement(kind="hex", nodes=row)


def femixed_section_rows(zone, section_index: int) -> list[list[int]]:
    metrics = zone.section_metrics(section_index)
    raw = zone.nodemap.section(section_index)[:]
    stride = int(metrics.num_nodes_per_elem)
    array = np.asarray(raw).reshape(-1, stride)
    return [[int(node) for node in row] for row in array]


def extract_femixed_volume_elements(zone) -> list[ClassicElement]:
    elements: list[ClassicElement] = []
    for section_index in range(zone.num_sections):
        metrics = zone.section_metrics(section_index)
        rows = femixed_section_rows(zone, section_index)
        if metrics.cell_shape == FECellShape.Tetrahedron:
            elements.extend(ClassicElement(kind="tet", nodes=row[:4]) for row in rows)
        elif metrics.cell_shape == FECellShape.Hexahedron:
            elements.extend(classify_fe_brick_element(row[:8]) for row in rows)
        elif metrics.cell_shape == FECellShape.Prism:
            elements.extend(ClassicElement(kind="prism", nodes=row[:6]) for row in rows)
        elif metrics.cell_shape == FECellShape.Pyramid:
            elements.extend(ClassicElement(kind="pyramid", nodes=row[:5]) for row in rows)
        elif metrics.cell_shape in {FECellShape.Triangle, FECellShape.Quadrilateral, FECellShape.Bar}:
            continue
        else:
            raise RuntimeError(f"Unsupported FEMixed volume cell shape: {metrics.cell_shape}")
    return elements


def extract_femixed_surface_faces(zone) -> list[list[int]]:
    faces: list[list[int]] = []
    for section_index in range(zone.num_sections):
        metrics = zone.section_metrics(section_index)
        rows = femixed_section_rows(zone, section_index)
        if metrics.cell_shape == FECellShape.Triangle:
            faces.extend([row[:3] for row in rows])
        elif metrics.cell_shape == FECellShape.Quadrilateral:
            faces.extend([row[:4] for row in rows])
        elif metrics.cell_shape in {FECellShape.Tetrahedron, FECellShape.Hexahedron, FECellShape.Prism, FECellShape.Pyramid, FECellShape.Bar}:
            continue
        else:
            raise RuntimeError(f"Unsupported FEMixed surface cell shape: {metrics.cell_shape}")
    return faces


def extract_classic_elements(zone) -> list[ClassicElement]:
    elements = []
    for element_index in range(zone.num_elements):
        nodemap_row = list(zone.nodemap[element_index])
        if zone.zone_type == ZoneType.FETetra:
            elements.append(ClassicElement(kind="tet", nodes=nodemap_row[:4]))
        elif zone.zone_type == ZoneType.FEBrick:
            elements.append(classify_fe_brick_element(nodemap_row))
        else:
            raise RuntimeError(f"Unsupported classic zone type: {zone.zone_type}")
    return elements


def extract_boundary_faces_from_classic_zone(
    elements: Sequence[ClassicElement],
    coordinates: Sequence[tuple[float, float, float]],
    boundary_type_index: int,
) -> list[BoundaryFace]:
    face_map: dict[tuple[int, ...], tuple[int, list[int]]] = {}
    for element_index, element in enumerate(elements):
        templates = CLASSIC_FACE_TEMPLATES[element.kind]
        for template in templates:
            face_nodes = [element.nodes[i] for i in template]
            oriented = orient_face_outward(face_nodes, coordinates, element.nodes)
            key = tuple(sorted(oriented))
            if key in face_map:
                del face_map[key]
            else:
                face_map[key] = (element_index, oriented)
    return [BoundaryFace(boundary_type_index, nodes=nodes) for _, nodes in face_map.values()]


def extract_poly_faces_for_element(zone, elementmap: Elementmap, element_index: int, coordinates: Sequence[tuple[float, float, float]]) -> PolyElement:
    facemap = zone.facemap
    element_faces = []
    unique_nodes = set()
    face_ids = list(elementmap.faces(element_index))
    provisional_nodes = set()
    for face_id in face_ids:
        node_count = facemap.num_nodes(face=face_id)
        for node_offset in range(node_count):
            provisional_nodes.add(facemap.node(face_id, node_offset))
    sorted_element_nodes = sorted(provisional_nodes)
    for face_id in face_ids:
        node_count = facemap.num_nodes(face=face_id)
        face_nodes = [facemap.node(face_id, node_offset) for node_offset in range(node_count)]
        oriented = orient_face_outward(face_nodes, coordinates, sorted_element_nodes)
        unique_nodes.update(oriented)
        element_faces.append(PolyFaceRecord(nodes=oriented, hanging_nodes=[]))
    return PolyElement(
        faces=element_faces,
        num_nodes_including_center_node=len(unique_nodes),
        center_node_number=-1,
    )


def extract_poly_zone(zone, boundary_type_index: int, coordinates: Sequence[tuple[float, float, float]]) -> tuple[list[BoundaryFace], list[PolyElement]]:
    facemap = zone.facemap
    elementmap = Elementmap(zone)
    poly_elements = [
        extract_poly_faces_for_element(zone, elementmap, element_index, coordinates)
        for element_index in range(zone.num_elements)
    ]

    boundary_faces = []
    for face_id in range(zone.num_faces):
        left_element = facemap.left_element(face_id)
        right_element = facemap.right_element(face_id)
        if left_element >= 0 and right_element >= 0:
            continue
        node_count = facemap.num_nodes(face=face_id)
        face_nodes = [facemap.node(face_id, node_offset) for node_offset in range(node_count)]
        owner_element = left_element if left_element >= 0 else right_element
        owner_nodes = sorted({node for poly_face in poly_elements[owner_element].faces for node in poly_face.nodes})
        oriented = orient_face_outward(face_nodes, coordinates, owner_nodes)
        boundary_faces.append(BoundaryFace(boundary_type_index, oriented))
    return boundary_faces, poly_elements


def extract_surface_faces(zone) -> list[list[int]]:
    if zone.zone_type == ZoneType.FEMixed:
        return extract_femixed_surface_faces(zone)
    if zone.zone_type == ZoneType.FETriangle:
        return [list(zone.nodemap[element_index][:3]) for element_index in range(zone.num_elements)]
    if zone.zone_type == ZoneType.FEQuad:
        faces = []
        for element_index in range(zone.num_elements):
            nodes = list(zone.nodemap[element_index])
            while len(nodes) > 3 and nodes[-1] == nodes[-2]:
                nodes.pop()
            faces.append(nodes)
        return faces
    if zone.zone_type == ZoneType.FEPolygon:
        facemap = zone.facemap
        elementmap = Elementmap(zone)
        faces = []
        for element_index in range(zone.num_elements):
            ordered_nodes = []
            for face_id in elementmap.faces(element_index):
                left_element = facemap.left_element(face_id)
                if left_element == element_index:
                    ordered_nodes.append(facemap.node(face_id, 0))
                else:
                    ordered_nodes.append(facemap.node(face_id, 1))
            faces.append(ordered_nodes)
        return faces
    raise RuntimeError(f"Unsupported surface zone type: {zone.zone_type}")


def coord_key(point: tuple[float, float, float]) -> tuple[float, float, float]:
    return (round(float(point[0]), 9), round(float(point[1]), 9), round(float(point[2]), 9))


def remap_classic_elements(elements: Sequence[ClassicElement], node_map: Sequence[int]) -> list[ClassicElement]:
    return [ClassicElement(kind=element.kind, nodes=[node_map[node] for node in element.nodes]) for element in elements]


def remap_poly_elements(elements: Sequence[PolyElement], node_map: Sequence[int]) -> list[PolyElement]:
    remapped = []
    for element in elements:
        remapped_faces = [
            PolyFaceRecord(
                nodes=[node_map[node] for node in face.nodes],
                hanging_nodes=[node_map[node] for node in face.hanging_nodes],
            )
            for face in element.faces
        ]
        remapped.append(
            PolyElement(
                faces=remapped_faces,
                num_nodes_including_center_node=element.num_nodes_including_center_node,
                center_node_number=node_map[element.center_node_number] + 1 if element.center_node_number >= 0 else -1,
            )
        )
    return remapped


def merge_selected_zones(selected_zones, x_name: str, y_name: str, z_name: str, nodal_variable_names: Sequence[str], boundary_types: Sequence[BoundaryType]) -> list[ZoneExport]:
    volume_zones = [zone for zone in selected_zones if is_supported_volume_zone(zone)]
    surface_zones = [zone for zone in selected_zones if is_supported_surface_zone(zone)]
    include_derived_volume_boundaries = len(surface_zones) == 0

    if not volume_zones:
        raise RuntimeError("At least one 3D volume FE zone is required for FVUNS export.")

    print(f"Merging {len(volume_zones)} volume zone(s) and {len(surface_zones)} surface zone(s) into one FVUNS grid.")

    coordinates: list[tuple[float, float, float]] = []
    node_lookup: dict[tuple[float, float, float], int] = {}
    nodal_results = [[] for _ in nodal_variable_names]
    classic_elements: list[ClassicElement] = []
    poly_elements: list[PolyElement] = []
    boundary_faces: list[BoundaryFace] = []

    for boundary_type_index, zone in enumerate(selected_zones, start=1):
        print(f"Extracting zone '{zone.name}'...")
        zone_coords = extract_coordinates(zone, x_name, y_name, z_name)
        zone_var_values = [list(zone.values(variable_name)[:]) for variable_name in nodal_variable_names]
        local_to_global = []

        for local_node_index, point in enumerate(zone_coords):
            key = coord_key(point)
            global_node_index = node_lookup.get(key)
            if global_node_index is None:
                global_node_index = len(coordinates)
                node_lookup[key] = global_node_index
                coordinates.append(point)
                for variable_index, values in enumerate(zone_var_values):
                    nodal_results[variable_index].append(values[local_node_index])
            local_to_global.append(global_node_index)

        if is_supported_volume_zone(zone):
            if zone.zone_type == ZoneType.FEPolyhedron:
                local_boundary_faces, local_poly_elements = extract_poly_zone(zone, boundary_type_index, zone_coords)
                poly_elements.extend(remap_poly_elements(local_poly_elements, local_to_global))
                if include_derived_volume_boundaries:
                    boundary_faces.extend(
                        BoundaryFace(boundary_type_index, [local_to_global[node] for node in face.nodes])
                        for face in local_boundary_faces
                    )
            elif zone.zone_type == ZoneType.FEMixed:
                local_classic_elements = extract_femixed_volume_elements(zone)
                classic_elements.extend(remap_classic_elements(local_classic_elements, local_to_global))
                if include_derived_volume_boundaries:
                    local_boundary_faces = extract_boundary_faces_from_classic_zone(local_classic_elements, zone_coords, boundary_type_index)
                    boundary_faces.extend(
                        BoundaryFace(boundary_type_index, [local_to_global[node] for node in face.nodes])
                        for face in local_boundary_faces
                    )
            else:
                local_classic_elements = extract_classic_elements(zone)
                classic_elements.extend(remap_classic_elements(local_classic_elements, local_to_global))
                if include_derived_volume_boundaries:
                    local_boundary_faces = extract_boundary_faces_from_classic_zone(local_classic_elements, zone_coords, boundary_type_index)
                    boundary_faces.extend(
                        BoundaryFace(boundary_type_index, [local_to_global[node] for node in face.nodes])
                        for face in local_boundary_faces
                    )
        else:
            surface_faces = extract_surface_faces(zone)
            boundary_faces.extend(
                BoundaryFace(boundary_type_index, [local_to_global[node] for node in face_nodes])
                for face_nodes in surface_faces
            )
            boundary_types[boundary_type_index - 1].clockness_flag = 0

        print(f"  nodes={zone.num_points}, mapped_nodes={len(local_to_global)}")

    merged_zone = ZoneExport(
        name="Merged Tecplot Zones",
        num_nodes=len(coordinates),
        coordinates=coordinates,
        boundary_faces=boundary_faces,
        classic_elements=classic_elements,
        poly_elements=poly_elements,
        nodal_results=nodal_results,
    )
    return [merged_zone]


def extract_coordinates(zone, x_name: str, y_name: str, z_name: str) -> list[tuple[float, float, float]]:
    x_values = zone.values(x_name)[:]
    y_values = zone.values(y_name)[:]
    z_values = zone.values(z_name)[:]
    return list(zip(x_values, y_values, z_values))


def collect_nodal_variable_names(dataset, zones, coordinate_variable_names: set[str]) -> list[str]:
    nodal_variables = []
    for variable_name in dataset.variable_names:
        if variable_name in coordinate_variable_names:
            continue
        if all(zone.values(variable_name).location == ValueLocation.Nodal for zone in zones):
            nodal_variables.append(variable_name)
    return nodal_variables


def extract_zone_export(zone, x_name: str, y_name: str, z_name: str, nodal_variable_names: Sequence[str], boundary_type_index: int) -> ZoneExport:
    print(f"Extracting zone '{zone.name}'...")
    coordinates = extract_coordinates(zone, x_name, y_name, z_name)
    classic_elements: list[ClassicElement] = []
    poly_elements: list[PolyElement] = []

    if zone.zone_type == ZoneType.FEPolyhedron:
        boundary_faces, poly_elements = extract_poly_zone(zone, boundary_type_index, coordinates)
    else:
        classic_elements = extract_classic_elements(zone)
        boundary_faces = extract_boundary_faces_from_classic_zone(classic_elements, coordinates, boundary_type_index)

    nodal_results = [list(zone.values(variable_name)[:]) for variable_name in nodal_variable_names]

    print(
        f"  nodes={zone.num_points}, boundary_faces={len(boundary_faces)}, "
        f"classic_elements={len(classic_elements)}, poly_elements={len(poly_elements)}"
    )

    return ZoneExport(
        name=zone.name,
        num_nodes=zone.num_points,
        coordinates=coordinates,
        boundary_faces=boundary_faces,
        classic_elements=classic_elements,
        poly_elements=poly_elements,
        nodal_results=nodal_results,
    )


def encode_elem_header(elem_type: int, wall_info: Sequence[int]) -> int:
    if elem_type == FVUNS_ELEMENT_TYPE["tet"]:
        header = 1 << ELEM_TYPE_BIT_SHIFT
        nfaces = 4
    elif elem_type == FVUNS_ELEMENT_TYPE["hex"]:
        header = 4 << ELEM_TYPE_BIT_SHIFT
        nfaces = 6
    elif elem_type == FVUNS_ELEMENT_TYPE["prism"]:
        header = 3 << ELEM_TYPE_BIT_SHIFT
        nfaces = 5
    elif elem_type == FVUNS_ELEMENT_TYPE["pyramid"]:
        header = 2 << ELEM_TYPE_BIT_SHIFT
        nfaces = 5
    else:
        raise RuntimeError(f"Unsupported standard element type for binary header: {elem_type}")

    for face_index in range(nfaces):
        wall_value = wall_info[face_index]
        if wall_value > A_WALL:
            raise RuntimeError(f"Invalid wall value in binary element header: {wall_value}")
        header |= wall_value << (face_index * BITS_PER_WALL)
    return header


def write_ints(stream, *values: int) -> None:
    stream.write(struct.pack("<" + "i" * len(values), *values))


def write_floats(stream, values: Sequence[float]) -> None:
    if values:
        stream.write(struct.pack("<" + "f" * len(values), *[float(value) for value in values]))


def write_str80(stream, value: str) -> None:
    stream.write(value.encode("ascii", errors="replace")[:80].ljust(80, b"\0"))


def classify_boundary_sections(boundary_faces: Sequence[BoundaryFace]) -> tuple[list[StandardBoundarySection], list[ArbitraryBoundarySection]]:
    standard_by_type: dict[int, list[list[int]]] = {}
    arbitrary_by_type: dict[int, list[list[int]]] = {}
    standard_order: list[int] = []
    arbitrary_order: list[int] = []

    for face in boundary_faces:
        nodes = [node + 1 for node in face.nodes]
        if len(nodes) <= 4:
            if face.boundary_type_index not in standard_by_type:
                standard_by_type[face.boundary_type_index] = []
                standard_order.append(face.boundary_type_index)
            standard_by_type[face.boundary_type_index].append(nodes + [0] * (4 - len(nodes)))
        else:
            if face.boundary_type_index not in arbitrary_by_type:
                arbitrary_by_type[face.boundary_type_index] = []
                arbitrary_order.append(face.boundary_type_index)
            arbitrary_by_type[face.boundary_type_index].append(nodes)

    standard_sections = [StandardBoundarySection(index, standard_by_type[index]) for index in standard_order]
    arbitrary_sections = [ArbitraryBoundarySection(index, arbitrary_by_type[index]) for index in arbitrary_order]
    return standard_sections, arbitrary_sections


def write_standard_elements_binary(stream, classic_elements: Sequence[ClassicElement]) -> None:
    if not classic_elements:
        return

    counts = {"tet": 0, "hex": 0, "prism": 0, "pyramid": 0}
    for element in classic_elements:
        counts[element.kind] += 1

    write_ints(stream, FV_ELEMENTS, counts["tet"], counts["hex"], counts["prism"], counts["pyramid"])
    for element in classic_elements:
        elem_type = FVUNS_ELEMENT_TYPE[element.kind]
        write_ints(stream, encode_elem_header(elem_type, [NOT_A_WALL] * MAX_NUM_ELEM_FACES))
        write_ints(stream, *[node + 1 for node in element.nodes])


def write_poly_elements_binary(stream, poly_elements: Sequence[PolyElement]) -> None:
    if not poly_elements:
        return

    write_ints(stream, FV_ARB_POLY_ELEMENTS, len(poly_elements))
    for element in poly_elements:
        write_ints(stream, len(element.faces), element.num_nodes_including_center_node, element.center_node_number)
        for face in element.faces:
            write_ints(stream, NOT_A_WALL, len(face.nodes))
            write_ints(stream, *[node + 1 for node in face.nodes])
            write_ints(stream, len(face.hanging_nodes))
            if face.hanging_nodes:
                write_ints(stream, *[node + 1 for node in face.hanging_nodes])


def write_combined_binary(
    path: Path,
    boundary_types: Sequence[BoundaryType],
    zones: Sequence[ZoneExport],
    nodal_variable_names: Sequence[str],
    time_value: float,
    fsmach: float,
    alpha: float,
    reynolds: float,
) -> None:
    print(f"Writing combined binary file: {path}")
    with path.open("wb") as stream:
        write_ints(stream, FV_MAGIC)
        write_str80(stream, "FIELDVIEW")
        write_ints(stream, FVUNS_VERSION_MAJOR, FVUNS_VERSION_MINOR, FV_COMBINED_FILE, 0)
        write_floats(stream, [time_value, fsmach, alpha, reynolds])

        write_ints(stream, len(zones))
        write_ints(stream, len(boundary_types))
        for boundary_type in boundary_types:
            write_ints(stream, boundary_type.surface_results_flag, boundary_type.clockness_flag)
            write_str80(stream, boundary_type.name)

        write_ints(stream, len(nodal_variable_names))
        for variable_name in nodal_variable_names:
            write_str80(stream, variable_name)

        write_ints(stream, 0)

        for zone in zones:
            standard_sections, arbitrary_sections = classify_boundary_sections(zone.boundary_faces)

            write_ints(stream, FV_NODES, zone.num_nodes)
            write_floats(stream, [xyz[0] for xyz in zone.coordinates])
            write_floats(stream, [xyz[1] for xyz in zone.coordinates])
            write_floats(stream, [xyz[2] for xyz in zone.coordinates])

            for section in standard_sections:
                write_ints(stream, FV_FACES, section.boundary_type_index, len(section.faces))
                for face in section.faces:
                    write_ints(stream, *face)

            for section in arbitrary_sections:
                write_ints(stream, FV_ARB_POLY_FACES, section.boundary_type_index, len(section.faces))
                for face in section.faces:
                    write_ints(stream, len(face))
                    write_ints(stream, *face)

            write_standard_elements_binary(stream, zone.classic_elements)
            write_poly_elements_binary(stream, zone.poly_elements)

            write_ints(stream, FV_VARIABLES)
            for variable_values in zone.nodal_results:
                write_floats(stream, variable_values)

            write_ints(stream, FV_BNDRY_VARS)
            write_ints(stream, FV_ARB_POLY_BNDRY_VARS)


def write_split_ascii_grid(path: Path, boundary_types: Sequence[BoundaryType], zones: Sequence[ZoneExport]) -> None:
    print(f"Writing grid file: {path}")
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(f"FieldView_Grids {FVUNS_VERSION_MAJOR} {FVUNS_VERSION_MINOR}\n")
        stream.write(f"Grids {len(zones)}\n")
        stream.write(f"Boundary Table {len(boundary_types)}\n")
        for boundary_type in boundary_types:
            stream.write(
                f"{boundary_type.wall_flag} {boundary_type.surface_results_flag} "
                f"{boundary_type.clockness_flag} {boundary_type.name}\n"
            )

        for zone in zones:
            stream.write(f"Nodes {zone.num_nodes}\n")
            for x, y, z in zone.coordinates:
                stream.write(f"{format_float(x)} {format_float(y)} {format_float(z)}\n")

            stream.write(f"Boundary Faces {len(zone.boundary_faces)}\n")
            for face in zone.boundary_faces:
                node_text = " ".join(str(node + 1) for node in face.nodes)
                stream.write(f"{face.boundary_type_index} {len(face.nodes)} {node_text}\n")

            stream.write("Elements\n")
            for element in zone.classic_elements:
                stream.write(f"{FVUNS_ELEMENT_TYPE[element.kind]} 1\n")
                stream.write(" ".join(str(node + 1) for node in element.nodes) + "\n")
            for element in zone.poly_elements:
                stream.write(f"{FVUNS_ELEMENT_TYPE['polyhedron']} 1\n")
                stream.write(
                    f"{len(element.faces)} {element.num_nodes_including_center_node} "
                    f"{element.center_node_number}\n"
                )
                for face in element.faces:
                    node_text = " ".join(str(node + 1) for node in face.nodes)
                    hanging_text = " ".join(str(node + 1) for node in face.hanging_nodes)
                    if hanging_text:
                        stream.write(f"{len(face.nodes)} {node_text} {len(face.hanging_nodes)} {hanging_text}\n")
                    else:
                        stream.write(f"{len(face.nodes)} {node_text} 0\n")


def write_split_ascii_results(
    path: Path,
    zones: Sequence[ZoneExport],
    nodal_variable_names: Sequence[str],
    time_value: float,
    fsmach: float,
    alpha: float,
    reynolds: float,
) -> None:
    print(f"Writing results file: {path}")
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(f"FieldView_Results {FVUNS_VERSION_MAJOR} {FVUNS_VERSION_MINOR}\n")
        stream.write("Constants\n")
        stream.write(
            f"{format_float(time_value)} {format_float(fsmach)} "
            f"{format_float(alpha)} {format_float(reynolds)}\n"
        )
        stream.write(f"Grids {len(zones)}\n")
        stream.write(f"Variable Names {len(nodal_variable_names)}\n")
        for variable_name in nodal_variable_names:
            stream.write(f"{variable_name[:80]}\n")
        stream.write("Boundary Variable Names 0\n")

        for zone in zones:
            stream.write(f"Nodes {zone.num_nodes}\n")
            if nodal_variable_names:
                stream.write("Variables\n")
                for variable_values in zone.nodal_results:
                    for value in variable_values:
                        stream.write(f"{format_float(value)}\n")
            stream.write("Boundary Variables\n")


def main() -> int:
    args = parse_args()
    if args.c:
        connect_to_tecplot(args.port)
        dataset = active_dataset()
    else:
        dataset = load_dataset_from_file(args.infile)
    print(f"Active dataset: {dataset.title}")
    print_zone_inventory(dataset)

    x_name = resolve_variable_name(dataset, args.xvar, ("X", "x", "CoordinateX"), "X")
    y_name = resolve_variable_name(dataset, args.yvar, ("Y", "y", "CoordinateY"), "Y")
    z_name = resolve_variable_name(dataset, args.zvar, ("Z", "z", "CoordinateZ"), "Z")
    print(f"Coordinate variables: X='{x_name}', Y='{y_name}', Z='{z_name}'")

    selected_zones = select_zones(dataset, args.zones)
    if not selected_zones:
        raise RuntimeError("No supported FE volume/surface zones were selected.")
    print(f"Selected {len(selected_zones)} supported zone(s).")

    coordinate_variable_names = {x_name, y_name, z_name}
    nodal_variable_names = collect_nodal_variable_names(dataset, selected_zones, coordinate_variable_names)
    print(f"Exporting {len(nodal_variable_names)} nodal result variable(s).")

    used_boundary_names: set[str] = set()
    boundary_types = []
    for zone_number, zone in enumerate(selected_zones, start=1):
        boundary_name = sanitize_boundary_name(zone.name or f"Zone_{zone_number}", used_boundary_names)
        boundary_types.append(BoundaryType(name=boundary_name))
    zone_exports = merge_selected_zones(
        selected_zones=selected_zones,
        x_name=x_name,
        y_name=y_name,
        z_name=z_name,
        nodal_variable_names=nodal_variable_names,
        boundary_types=boundary_types,
    )

    output_path = Path(args.outfile)
    if output_path.suffix == "":
        output_path = output_path.with_name(output_path.name + ".fvuns")

    write_combined_binary(
        output_path,
        boundary_types,
        zone_exports,
        nodal_variable_names,
        time_value=args.time,
        fsmach=args.fsmach,
        alpha=args.alpha,
        reynolds=args.re,
    )

    print(f"Wrote {output_path}")
    if not nodal_variable_names:
        print("No nodal result variables were exported.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

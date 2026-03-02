#!/usr/bin/env python3
"""USAGE:
Read TOUGH flow.inp file OR read MESH/INCON and build prefix-based layer groups with connectivity. 
Constructs Tecplot zones with this data and writes presents the data in connected mode or writes it to plt.

Execute script with no arguments or use -h to see all args.
"""

import argparse
import sys
from pathlib import Path

import tecplot as tp
from tecplot.constant import *
import numpy as np


# ---- CONSTANTS -----
VOLUME_CUTOFF = 1e30


# ---- HELPERS ------
class Element:
    def __init__(self, elem_id, layer_prefix, rock_id, volume, x, y, z):
        self.elem_id = elem_id
        self.layer_prefix = layer_prefix
        self.rock_id = rock_id
        self.volume = volume
        self.x = x
        self.y = y
        self.z = z

def _safe_float(text):
    text = text.strip()
    if not text:
        return float("nan")
    if "*" in text:
        return float("nan")
    try:
        return float(text.replace("D", "E").replace("d", "E"))
    except ValueError:
        return float("nan")

def _sanitize_volume(value: float) -> float:
    # TOUGH3 uses extremely large volumes (e.g., 1e50) for boundary/inactive elements.
    if value != value:
        return value
    if value > VOLUME_CUTOFF:
        return float("nan")
    return value

def _float_list(tokens):
    values = []
    for token in tokens:
        try:
            values.append(float(token))
        except ValueError:
            continue
    return values


# -- PARSE AND BUILD LAYERS --
def parse_incon(incon_path):
    """
    Parse INCON and return element_id -> list of values (usually 8).
    """
    data = {}
    in_incon = False

    with incon_path.open("r", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            tag = line.strip()
            if not tag:
                continue
            if tag == "INCON":
                in_incon = True
                continue
            if not in_incon:
                continue

            elem_id = line[:5].strip()
            tokens = line[5:].split()
            if elem_id:
                data[elem_id] = _float_list(tokens)
                continue

            if data:
                last_id = next(reversed(data))
                data[last_id].extend(_float_list(tokens))

    return data

def parse_mesh(mesh_path):
    elements = {}
    edges = []

    in_eleme = False
    in_conne = False

    with mesh_path.open("r", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            tag = line.strip()

            if tag == "ELEME":
                in_eleme = True
                in_conne = False
                continue
            if tag == "CONNE":
                in_eleme = False
                in_conne = True
                continue
            if not tag:
                continue

            row = line.ljust(80)

            if in_eleme:
                elem_id = row[0:5]
                layer_prefix = elem_id[:2]
                rock_id = row[15:20].strip() or "UNK"
                volume = _sanitize_volume(_safe_float(row[20:30]))
                x = _safe_float(row[50:60])
                y = _safe_float(row[60:70])
                z = _safe_float(row[70:80])
                elements[elem_id] = Element(
                    elem_id=elem_id,
                    layer_prefix=layer_prefix,
                    rock_id=rock_id,
                    volume=volume,
                    x=x,
                    y=y,
                    z=z,
                )

            elif in_conne:
                e1 = row[0:5]
                e2 = row[5:10]
                if e1 and e2:
                    edges.append((e1, e2))

    return elements, edges

def parse_flow(flow_path):
    elements = {}
    edges = []
    incon = {}

    in_eleme = False
    in_conne = False
    in_incon = False

    with flow_path.open("r", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            tag = line.strip()

            if tag.startswith("ELEME"):
                in_eleme = True
                in_conne = False
                in_incon = False
                continue
            if tag.startswith("CONNE"):
                in_eleme = False
                in_conne = True
                in_incon = False
                continue
            if tag.startswith("INCON"):
                in_eleme = False
                in_conne = False
                in_incon = True
                continue
            if in_incon and tag.startswith("END"):
                break
            if not tag:
                continue

            row = line.ljust(80)

            if in_eleme:
                elem_id = row[0:5]
                layer_prefix = elem_id[:2]
                rock_id = row[15:20].strip() or "UNK"
                # TOUGH fixed-width ELEME fields: volume is columns 21-30.
                volume = _sanitize_volume(_safe_float(row[20:30]))
                x = _safe_float(row[50:60])
                y = _safe_float(row[60:70])
                z = _safe_float(row[70:80])
                elements[elem_id] = Element(
                    elem_id=elem_id,
                    layer_prefix=layer_prefix,
                    rock_id=rock_id,
                    volume=volume,
                    x=x,
                    y=y,
                    z=z,
                )

            elif in_conne:
                e1 = row[0:5]
                e2 = row[5:10]
                if e1 and e2:
                    edges.append((e1, e2))
            elif in_incon:
                if line.strip().startswith("END"):
                    break
                if "----" in line:
                    in_incon = False
                    continue
                elem_id = line[:5].strip()
                tokens = line[5:].split()
                if elem_id:
                    values = _float_list(tokens)
                    incon[elem_id] = values
                    continue
                if incon:
                    last_id = next(reversed(incon))
                    incon[last_id].extend(_float_list(tokens))

    return elements, edges, incon

def build_layers(elements, edges):
    by_layer = {}

    for elem in elements.values():
        layer = by_layer.setdefault(
            elem.layer_prefix,
            {
                "layer_prefix": elem.layer_prefix,
                "elements": [],
                "edges": [],
            },
        )
        layer["elements"].append(
            {
                "id": elem.elem_id,
                "rock_id": elem.rock_id,
                "x": float(elem.x),
                "y": float(elem.y),
                "z": float(elem.z),
                "volume": elem.volume,
            }
        )

    seen_internal_edges = {k: set() for k in by_layer}
    for a, b in edges:
        ea = elements.get(a)
        eb = elements.get(b)
        if ea is None or eb is None:
            continue

        if ea.layer_prefix != eb.layer_prefix:
            continue

        layer_key = ea.layer_prefix
        key = (a, b) if a <= b else (b, a)
        if key in seen_internal_edges[layer_key]:
            continue
        seen_internal_edges[layer_key].add(key)

        by_layer[layer_key]["edges"].append({"a": key[0], "b": key[1]})

    return sorted(by_layer.values(), key=lambda d: d["layer_prefix"])

def attach_incon(layers, incon):
    for layer in layers:
        for elem in layer["elements"]:
            # There is often a space in the eleme section, ensure we are grabbing the same element.
            elem_id = elem["id"].strip()
            if elem_id in incon:
                values = incon[elem_id]
                elem["pressure"] = values[0] if len(values) > 0 else float("nan")
                elem["temperature"] = values[1] if len(values) > 1 else float("nan")
                elem["saturation"] = values[2] if len(values) > 2 else float("nan")
                elem["mass_fraction"] = values[3] if len(values) > 3 else float("nan")

def get_layers(flow_path=None, mesh_path=None, incon_path=None):
    if flow_path:
        fpath = Path(flow_path)
        elements, edges, incon = parse_flow(fpath)
        layers = build_layers(elements, edges)
        attach_incon(layers, incon)
        return layers

    if mesh_path:
        mpath = Path(mesh_path)
        elements, edges = parse_mesh(mpath)
        layers = build_layers(elements, edges)
        if incon_path:
            ipath = Path(incon_path)
            incon = parse_incon(ipath)
            attach_incon(layers, incon)
        return layers

    raise ValueError("\n\n Provide either flow_path OR mesh_path (with optional incon_path). \n")



# ------ TECPLOT --------
def create_tecplot_dataset(layers, vor):
    # id and rock_id are non-numeric... maybe add as aux data...?
    tecplot_vars = [k for k in layers[0].get("elements")[0].keys() if k not in ("id", "rock_id")]
    if vor and "avgz" not in tecplot_vars:
        # insert avgz after y so that it's the 3rd var...
        if "y" in tecplot_vars:
            y_idx = tecplot_vars.index("y")
            tecplot_vars.insert(y_idx + 1, "avgz")
        else:
            tecplot_vars.append("avgz")
    tp.new_layout()

    frame = tp.active_frame()
    frame.create_dataset("Data")
    ds = frame.dataset

    dummy_var  = ds.add_variable("dummyvar")
    dummy_zone = ds.add_ordered_zone("dummyzone", shape=(1,1,1))
    
    for v in tecplot_vars:
        if not vor:
            ds.add_variable(v, locations=ValueLocation.Nodal)
        else:
            if v in ['x', 'y', 'avgz']:
                ds.add_variable(v, locations=ValueLocation.Nodal)
            else:
                ds.add_variable(v, locations=ValueLocation.CellCentered)
    
    with tp.session.suspend():
        if vor:
            print("Constructing Voronoi meshes \n")
        for l in layers:
            zone_from_layer(l, frame, tecplot_vars, vor)
    
    if dummy_zone is not None:
        ds.delete_zones(dummy_zone)
        ds.delete_variables(dummy_var)
    return

def set_tecplot_view(vor: bool):
    frame = ds = tp.active_frame()
    ds = frame.dataset
    
    if len(list(ds.zones())) < 2:
        frame.plot_type = PlotType.Cartesian2D
        plot = tp.active_frame().plot()

    else:
        frame.plot_type = PlotType.Cartesian3D
        plot = tp.active_frame().plot()
        if vor:
            plot.axes.z_axis.variable = ds.variable('avgz')
        else:
            plot.axes.z_axis.variable = ds.variable('z')
    
    plot.axes.x_axis.variable = ds.variable('x')
    plot.axes.y_axis.variable = ds.variable('y')
    return

def zone_from_layer(layer: dict, frame: tp.layout.Frame, var_list, vor: bool):
    layer_name = f"Layer {list(layer.values())[0]}"
    elems = list(layer.values())[1]
    ds = frame.dataset

    # VORONOI workflow...
    if vor:
        vor_info = build_voronoi_layer(layer)
        # Vor returns:
        # "voronoi": vor, "points": points3d,
        # "elements": elems, "z_avg": z_avg, "elementmap": elementmap,
        # "num_faces": num_faces
        points = vor_info.get("points")
        elementmap = vor_info.get("elementmap")
        num_faces = vor_info.get("num_faces")
        elems = vor_info.get("elements")
        z = ds.add_poly_zone(ZoneType.FEPolygon,
                             layer_name, 
                             num_points=len(points), 
                             num_elements=len(elems),
                             num_faces=num_faces)

    # Triangulation workflow...
    else:
        elems = [e for e in elems if (e.get('volume') <= VOLUME_CUTOFF) and (e.get('volume') == e.get('volume'))]
        z = ds.add_ordered_zone(layer_name, (len(elems), 1, 1))
    
    # assign var values...
    for var in var_list[:]:
        if vor and var in ['x','y','avgz']:
            col = {"x": 0, "y": 1, "avgz": 2}[var]
            z.values(var)[:] = points[:, col]
        else:
            z.values(var)[:] = [e[var] for e in elems]

    if vor:
        z.facemap.set_elementmap(elementmap)

    # Triangulation and housekeeping...
    if not vor:
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()
        plot.axes.x_axis.variable = ds.variable('x')
        plot.axes.y_axis.variable = ds.variable('y')

        tp.macro.execute_command(f'''
                                $!Triangulate 
                                SourceZones =  [{z.index+1}]
                                BoundaryZones =  []
                                UseBoundary = No
                                IncludeBoundaryPts = No
                                TriangleKeepFactor = 0.25''')
        tri_zone = ds.zone(-1)
        tri_zone.name = layer_name
        ds.delete_zones(z)


# --- VORONOI BUILDER ---
def _clip_polygon_to_bbox(poly, xmin, xmax, ymin, ymax):
    def clip(poly, edge):
        out = []
        if not poly:
            return out
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i + 1) % len(poly)]
            inside1 = edge["inside"](p1)
            inside2 = edge["inside"](p2)
            if inside1 and inside2:
                out.append(p2)
            elif inside1 and not inside2:
                out.append(edge["intersect"](p1, p2))
            elif not inside1 and inside2:
                out.append(edge["intersect"](p1, p2))
                out.append(p2)
        return out

    edges = [
        {
            "inside": lambda p: p[0] >= xmin,
            "intersect": lambda p1, p2: (xmin, p1[1] + (p2[1]-p1[1]) * (xmin - p1[0]) / (p2[0]-p1[0]))
            if p2[0] != p1[0] else (xmin, p1[1]),
        },
        {
            "inside": lambda p: p[0] <= xmax,
            "intersect": lambda p1, p2: (xmax, p1[1] + (p2[1]-p1[1]) * (xmax - p1[0]) / (p2[0]-p1[0]))
            if p2[0] != p1[0] else (xmax, p1[1]),
        },
        {
            "inside": lambda p: p[1] >= ymin,
            "intersect": lambda p1, p2: (p1[0] + (p2[0]-p1[0]) * (ymin - p1[1]) / (p2[1]-p1[1]), ymin)
            if p2[1] != p1[1] else (p1[0], ymin),
        },
        {
            "inside": lambda p: p[1] <= ymax,
            "intersect": lambda p1, p2: (p1[0] + (p2[0]-p1[0]) * (ymax - p1[1]) / (p2[1]-p1[1]), ymax)
            if p2[1] != p1[1] else (p1[0], ymax),
        },
    ]

    out = _dedupe_poly_tol(poly, 1e-9)
    for edge in edges:
        out = clip(out, edge)
        out = _dedupe_poly_tol(out, 1e-9)
        if not out:
            break
    return out

def _voronoi_finite_polygons_2d(vor, radius: float | None = None, bounds=None):
    """
    Reconstruct finite Voronoi polygons in 2D from a Voronoi diagram.
    Returns (regions, vertices), where regions is a list of lists of vertex
    indices (one per input point) and vertices is an (M,2) array.
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Voronoi input must be 2D.")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max() * 2.0

    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    for p1, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]

        if all(v >= 0 for v in region):
            new_regions.append(region)
            continue

        ridges = all_ridges.get(p1, [])
        new_region = [v for v in region if v >= 0]

        for p2, v1, v2 in ridges:
            if v1 >= 0 and v2 >= 0:
                continue

            v = v1 if v1 >= 0 else v2
            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v] + direction * radius

            new_vertices.append(far_point.tolist())
            new_region.append(len(new_vertices) - 1)

        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]

        if bounds is not None:
            xmin, xmax, ymin, ymax = bounds
            poly = [tuple(new_vertices[v]) for v in new_region]
            poly = _clip_polygon_to_bbox(poly, xmin, xmax, ymin, ymax)
            if not poly:
                new_regions.append([])
                continue
            new_region = []
            for pt in poly:
                try:
                    idx = new_vertices.index(list(pt))
                except ValueError:
                    new_vertices.append([pt[0], pt[1]])
                    idx = len(new_vertices) - 1
                new_region.append(idx)
        new_regions.append(new_region)

    return new_regions, np.asarray(new_vertices, dtype=float)

def _num_unique_faces(elementmap):
    faces = set()
    for poly in elementmap:
        if len(poly) < 2:
            continue
        for i in range(len(poly)):
            a = poly[i]
            b = poly[(i + 1) % len(poly)]
            key = (a, b) if a <= b else (b, a)
            faces.add(key)
    return len(faces)

def _polygon_area_2d(poly):
    if len(poly) < 3:
        return 0.0
    area = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return 0.5 * area

def _dedupe_poly_tol(poly, eps):
    if not poly:
        return []
    out = []
    for p in poly:
        if not out:
            out.append(p)
            continue
        if abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) <= eps and abs(out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out

def _clean_polygon(poly, eps, min_edge, min_quality, bounds, drop_boundary):
    # remove near-duplicate points anywhere in the loop while preserving order
    cleaned = []
    for p in poly:
        if all(abs(p[0] - q[0]) > eps or abs(p[1] - q[1]) > eps for q in cleaned):
            cleaned.append(p)
    cleaned = _dedupe_poly_tol(cleaned, eps)
    if len(cleaned) < 3:
        return []
    area = _polygon_area_2d(cleaned)
    if abs(area) <= eps:
        return []
    # drop very skinny polygons
    perim = 0.0
    min_len = None
    for i in range(len(cleaned)):
        x1, y1 = cleaned[i]
        x2, y2 = cleaned[(i + 1) % len(cleaned)]
        dx = x2 - x1
        dy = y2 - y1
        l = (dx * dx + dy * dy) ** 0.5
        perim += l
        min_len = l if min_len is None else min(min_len, l)
    if min_len is not None and min_len < min_edge:
        return []
    if perim > 0.0:
        quality = abs(area) / (perim * perim)
        if quality < min_quality:
            return []
    if drop_boundary and bounds is not None:
        xmin, xmax, ymin, ymax = bounds
        for x, y in cleaned:
            if abs(x - xmin) <= eps or abs(x - xmax) <= eps or abs(y - ymin) <= eps or abs(y - ymax) <= eps:
                return []
    if area < 0:
        cleaned.reverse()
    return cleaned

def build_voronoi_layer(layer: dict):
    """
    Build a 2D Voronoi tessellation from element centers in a single layer.
    Returns a dict with points (3D vertices),
    and elements (original cell centers/values).

    Returns: 
    {   "voronoi": vor,
        "points": points3d,
        "elements": elems,
        "z_avg": z_avg }
    """
    from scipy.spatial import Voronoi

    # CRITICAL: 
    # Would user want elements to lie in 2D plane or 
    # at orginal Z-values, outside the plane...
    elems = layer["elements"]
    points2d = np.array([(e["x"], e["y"]) for e in elems], dtype=float)
    if len(points2d) < 3:
        raise ValueError("Voronoi requires at least 3 non-collinear points.")

    vor = Voronoi(points2d)
    z_avg = float(np.mean([e["z"] for e in elems])) if elems else float("nan")

    xmin = float(points2d[:, 0].min())
    xmax = float(points2d[:, 0].max())
    ymin = float(points2d[:, 1].min())
    ymax = float(points2d[:, 1].max())
    pad_x = (xmax - xmin) * 0.01
    pad_y = (ymax - ymin) * 0.01
    bounds = (xmin - pad_x, xmax + pad_x, ymin - pad_y, ymax + pad_y)

    regions, verts2d = _voronoi_finite_polygons_2d(vor, bounds=bounds)

    span = max(xmax - xmin, ymax - ymin, 1.0)
    eps = span * 1e-9
    min_edge = span * 1e-6
    min_quality = 1e-8

    # Build cleaned polygons without global vertex merging to avoid topology errors.
    points2d = []
    elementmap = []
    kept_elems = []

    for i, elem in enumerate(elems):
        region = regions[i] if i < len(regions) else []
        if not region:
            continue
        poly = [tuple(verts2d[v]) for v in region]
        poly = _clean_polygon(poly, eps, min_edge, min_quality, bounds, True)
        if not poly:
            continue

        poly_idx = []
        for x, y in poly:
            idx = len(points2d)
            points2d.append((x, y))
            poly_idx.append(idx)

        if len(poly_idx) < 3:
            continue
        elementmap.append(poly_idx)
        kept_elems.append(elem)

    points3d = np.column_stack((np.array(points2d, dtype=float), np.full(len(points2d), z_avg)))
    num_faces = _num_unique_faces(elementmap)

    return {
        "voronoi": vor,
        "points": points3d,
        "elements": kept_elems,
        "elementmap": elementmap,
        "num_faces": num_faces,
        "z_avg": z_avg,
    }



def main():
    parser = argparse.ArgumentParser(description="Build prefix-based TOUGH layers from flow.inp or MESH/INCON")
    parser.add_argument("--flow", default=None, help="Path to flow.inp (preferred when provided)")
    parser.add_argument("--mesh", default=None, help="Path to MESH")
    parser.add_argument("--voronoi", action="store_true", default=False, help="Construct polygonal Voronoi layers like TOUGHREACT/PetraSim instead of triangulated node-based layers.")
    parser.add_argument("--incon", default=None, help="Optional INCON path")
    parser.add_argument("--write", default=None, help="Path to write out the resulting Tecplot data")
    parser.add_argument("--connected", action="store_true", default=False, help="Whether to run this in Tecplot 360. Allows for visualization of data")
    
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.flow and (args.mesh or args.incon):
        raise SystemExit("Use either --flow or --mesh/--incon, not both.")
    layers = get_layers(args.flow, args.mesh, args.incon)
    
    if args.connected:
        if args.write:
            raise SystemExit("Use either --write or --connected, not both.")
        else:
            tp.session.connect()
    else:
        if not args.write:
            raise SystemExit("\n Use --write to save the resulting data OR --connected to view in Tecplot 360 connected mode. \n")
        
    for layer in layers[:]:
        print(
            f"prefix={layer['layer_prefix']!r} "
            f"elements={len(layer['elements'])} "
            f"intra_edges={len(layer['edges'])}"
        )

    print("\nCreating Tecplot 360 dataset \n")
    create_tecplot_dataset(layers, args.voronoi)
    
    print("Setting plot view\n")
    set_tecplot_view(args.voronoi)
    if args.write:
        print("Writing file to PLT \n")
        tp.data.save_tecplot_plt(args.write)

if __name__ == "__main__":
    main()

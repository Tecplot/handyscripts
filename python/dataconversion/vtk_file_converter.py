"""
This script runs in batch mode and converts files readable by VTK (.vtu, .vtp,
.vts, .vti, .pdb, .xmf, .xdmf) to Tecplot PLT format. This file may also be
imported and used as a module (see example usage in pvd_file_converter.py).


Additional Python modules needed:
---------------------------------
numpy
    A general-purpose array-processing package. See more info here:
    https://pypi.org/project/numpy/
os
    A module that provides functions to interact with the operating system. It
    is installed with Python.
tecplot
    The PyTecplot module. See installation and documenation here:
    https://www.tecplot.com/docs/pytecplot/install.html
time
    A module providing time related functions. It is installed with Python.
vtk
    A package that supports reading of vtk data. VTK is an open-source toolkit
    for 3D computer graphics, image processing, and visualization.
    https://pypi.org/project/vtk/
    NOTE: vtk 9.3.0 or newer is required for VTKHDF support


Example usage:
--------------
Windows:
    > python vtk_file_converter.py 'Fluid Domain.vtu' converted_vtu_file.plt

MacOS/Linux:
    > '/Applications/Tecplot 360 EX 2021 R2/bin/tec360-env' -- python3 vtk_file_converter.py 1hc8.pdb converted_pdb.plt

Known script limitations/issues:
--------------------------------
 - Poly data left/right elements aren't set correctly. This can cause issues
   with polyhedral shading.
 - Quadratic elements are imported as linear elements
 - Currently supported file formats: .vtk, .vtu, .vtp, .vts, .vti, .vtkhdf,
   .hdf, .pdb, .xmf, .xdmf

 - If you have any comments about this script, let us know at support@tecplot.com,
   or if you have improvements, send us a Pull Request!
   https://github.com/Tecplot/handyscripts
"""

import os
import numpy as np
import vtk
import tecplot as tp
from tecplot.constant import *
import time


DEFAULT_ZONE_NAME = "NO ZONE NAME"
COORDINATE_VARIABLE_NAMES = ('x', 'y', 'z')


def field_data_type(vtk_data_type):
    type_dict = dict()
    type_dict[vtk.VTK_BIT]           = FieldDataType.Bit
    type_dict[vtk.VTK_CHAR]          = FieldDataType.Byte
    type_dict[vtk.VTK_UNSIGNED_CHAR] = FieldDataType.Byte
    type_dict[vtk.VTK_SIGNED_CHAR]   = FieldDataType.Int16
    type_dict[vtk.VTK_INT]           = FieldDataType.Int16
    type_dict[vtk.VTK_UNSIGNED_INT]  = FieldDataType.Int16
    type_dict[vtk.VTK_LONG]          = FieldDataType.Int32
    type_dict[vtk.VTK_LONG_LONG]     = FieldDataType.Int32
    type_dict[vtk.VTK_UNSIGNED_LONG] = FieldDataType.Int32
    type_dict[vtk.VTK_ID_TYPE]       = FieldDataType.Int32
    type_dict[vtk.VTK_FLOAT]         = FieldDataType.Float
    type_dict[vtk.VTK_DOUBLE]        = FieldDataType.Double
    return type_dict[vtk_data_type]

def component_variable_name(name, num_components, component):
    if num_components == 1:
        return name

    # Special case for 3 & 6 components to match ParaView's behavior
    if num_components == 3:
        suffix = ['_X', '_Y', '_Z']
    elif num_components == 6:
        suffix = ['_XX', '_YY', '_ZZ', '_XY', '_YZ', '_XZ']
    else:
        # Otherwise use '_1', '_2', '_3', etc. for the suffix.
        suffix = ["_"+str(i+1) for i in range(num_components)]
    return name+suffix[component]

def vtk_data_specs(data, location):
    specs = []
    for i in range(data.GetNumberOfArrays()):
        arr = data.GetArray(i)
        if arr == None:
            continue

        fd_type = field_data_type(arr.GetDataType())
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            specs.append((component_variable_name(name, num_components, component), fd_type, location))
    return specs

def image_data_specs(vtk_dataset):
    specs = []
    pd = vtk_dataset.GetPointData()
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        if arr == None:
            continue
        specs.append((arr.GetName(), field_data_type(arr.GetDataType()), ValueLocation.Nodal))
    return specs

def add_occurrence_keys(specs):
    counts = dict()
    keyed_specs = []
    for name, fd_type, location in specs:
        occurrence = counts.get(name, 0)
        counts[name] = occurrence + 1
        keyed_specs.append((name, occurrence, fd_type, location))
    return keyed_specs

def has_default_coordinate_variables(tecplot_dataset):
    if tecplot_dataset.num_variables < 3:
        return False
    return tecplot_dataset.variable_names[:3] == list(COORDINATE_VARIABLE_NAMES)

def coordinate_specs():
    return [(name, FieldDataType.Float, ValueLocation.Nodal) for name in COORDINATE_VARIABLE_NAMES]

def coordinate_name_counts(tecplot_dataset):
    counts = dict()
    if has_default_coordinate_variables(tecplot_dataset):
        for name in COORDINATE_VARIABLE_NAMES:
            counts[name] = counts.get(name, 0) + 1
    return counts

def add_variable(tecplot_dataset, name, fd_type=None, location=None):
    kwargs = dict()
    if fd_type is not None:
        kwargs['dtypes'] = [fd_type] if tecplot_dataset.num_zones == 0 else fd_type
    if location is not None:
        kwargs['locations'] = [location] if tecplot_dataset.num_zones == 0 else location
    return tecplot_dataset.add_variable(name, **kwargs)

def ensure_coordinate_variables(tecplot_dataset):
    if tecplot_dataset.num_variables == 0:
        for name in COORDINATE_VARIABLE_NAMES:
            add_variable(tecplot_dataset, name, FieldDataType.Float, ValueLocation.Nodal)

def dataset_variable_keys(tecplot_dataset):
    counts = dict()
    for i, name in enumerate(tecplot_dataset.variable_names):
        occurrence = counts.get(name, 0)
        counts[name] = occurrence + 1
        yield i, (name, occurrence)

def get_variable_by_occurrence(tecplot_dataset, name, occurrence):
    count = 0
    for i, variable_name in enumerate(tecplot_dataset.variable_names):
        if variable_name == name:
            if count == occurrence:
                return tecplot_dataset.variable(i)
            count += 1
    return None

def ensure_variables(tecplot_dataset, keyed_specs):
    existing_name_counts = dict()
    for name in tecplot_dataset.variable_names:
        existing_name_counts[name] = existing_name_counts.get(name, 0) + 1

    for name, occurrence, fd_type, location in keyed_specs:
        while existing_name_counts.get(name, 0) <= occurrence:
            add_variable(tecplot_dataset, name, fd_type, location)
            existing_name_counts[name] = existing_name_counts.get(name, 0) + 1

def existing_variable_type_and_location(tecplot_dataset, variable_index):
    if tecplot_dataset.num_zones == 0:
        return FieldDataType.Float, ValueLocation.Nodal

    zone = tecplot_dataset.zone(0)
    array = zone.values(variable_index)
    return array.data_type, array.location

def zone_variable_layout(tecplot_dataset, keyed_specs):
    spec_lookup = dict()
    for name, occurrence, fd_type, location in keyed_specs:
        spec_lookup[(name, occurrence)] = (fd_type, location)

    dtypes = []
    locations = []
    for variable_index, variable_key in dataset_variable_keys(tecplot_dataset):
        if variable_key in spec_lookup:
            fd_type, location = spec_lookup[variable_key]
        elif variable_index < 3:
            fd_type, location = existing_variable_type_and_location(tecplot_dataset, variable_index)
            location = ValueLocation.Nodal
        else:
            fd_type, location = existing_variable_type_and_location(tecplot_dataset, variable_index)
        dtypes.append(fd_type)
        locations.append(location)
    return dtypes, locations

def prepare_vtk_dataset_variables(vtk_dataset, tecplot_dataset, include_cell_data=True):
    ensure_coordinate_variables(tecplot_dataset)

    specs = []
    if has_default_coordinate_variables(tecplot_dataset):
        specs.extend(coordinate_specs())
    specs.extend(vtk_data_specs(vtk_dataset.GetPointData(), ValueLocation.Nodal))
    if include_cell_data:
        specs.extend(vtk_data_specs(vtk_dataset.GetCellData(), ValueLocation.CellCentered))

    keyed_specs = add_occurrence_keys(specs)
    ensure_variables(tecplot_dataset, keyed_specs)
    return keyed_specs

def prepare_image_data_variables(vtk_dataset, tecplot_dataset):
    ensure_coordinate_variables(tecplot_dataset)

    specs = []
    if has_default_coordinate_variables(tecplot_dataset):
        specs.extend(coordinate_specs())
    specs.extend(image_data_specs(vtk_dataset))

    keyed_specs = add_occurrence_keys(specs)
    ensure_variables(tecplot_dataset, keyed_specs)
    return keyed_specs

def get_vtk_reader(vtk_file):
    vtk_file_lower = vtk_file.lower()
    if vtk_file_lower.endswith(".vtk"):
        return vtk.vtkDataSetReader()
    elif vtk_file_lower.endswith(".vtu"):
        return vtk.vtkXMLUnstructuredGridReader()
    elif vtk_file_lower.endswith(".vtp"):
        return vtk.vtkXMLPolyDataReader()
    elif vtk_file_lower.endswith(".vts"):
        return vtk.vtkXMLStructuredGridReader()
    elif vtk_file_lower.endswith(".vti"):
        return vtk.vtkXMLImageDataReader()
    elif vtk_file_lower.endswith(".pdb"):
        return vtk.vtkPDBReader()
    elif vtk_file_lower.endswith(".vtkhdf") or vtk_file_lower.endswith(".hdf"):
        return vtk.vtkHDFReader()
    elif vtk_file_lower.endswith(".xmf") or vtk_file_lower.endswith(".xdmf"):
        return vtk.vtkXdmfReader()

    raise ValueError("Unsupported VTK file type: {}".format(vtk_file))

def reader_time_steps(reader):
    info = reader.GetOutputInformation(0)
    key = vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS()
    if not info or not info.Has(key):
        return []
    return [info.Get(key, i) for i in range(info.Length(key))]

def metadata_name(metadata):
    if metadata and metadata.Has(vtk.vtkCompositeDataSet.NAME()):
        return metadata.Get(vtk.vtkCompositeDataSet.NAME())
    return None

def is_composite_dataset(vtk_dataset):
    return vtk_dataset and vtk_dataset.IsA("vtkCompositeDataSet")

def add_composite_dataset(vtk_dataset, tecplot_dataset, zone_name=None):
    zones = []
    iterator = vtk_dataset.NewIterator()
    iterator.SkipEmptyNodesOn()
    iterator.VisitOnlyLeavesOn()
    iterator.InitTraversal()

    block_number = 0
    while not iterator.IsDoneWithTraversal():
        block = iterator.GetCurrentDataObject()
        block_name = None
        if iterator.HasCurrentMetaData():
            block_name = metadata_name(iterator.GetCurrentMetaData())
        if not block_name:
            parent_name = zone_name if zone_name else vtk_dataset.GetClassName()
            block_name = "{} Block {}".format(parent_name, block_number)
        zones.extend(add_vtk_dataset(block, tecplot_dataset, block_name))
        block_number += 1
        iterator.GoToNextItem()
    return zones

def zone_type(vtk_cell_type):
    print("Cell Type:", vtk_cell_type)
    type_dict = dict()
    type_dict[vtk.VTK_LINE] = ZoneType.FELineSeg
    type_dict[vtk.VTK_TRIANGLE] = ZoneType.FETriangle
    type_dict[vtk.VTK_QUADRATIC_TRIANGLE] = ZoneType.FETriangle
    type_dict[vtk.VTK_QUAD]     = ZoneType.FEQuad
    type_dict[vtk.VTK_TETRA]    = ZoneType.FETetra
    type_dict[vtk.VTK_QUADRATIC_TETRA]    = ZoneType.FETetra
    type_dict[vtk.VTK_VOXEL] = ZoneType.FEBrick
    type_dict[vtk.VTK_HEXAHEDRON] = ZoneType.FEBrick
    type_dict[vtk.VTK_LAGRANGE_HEXAHEDRON] = ZoneType.FEBrick
    # Special code to create collapsed bricks
    type_dict[vtk.VTK_WEDGE] = ZoneType.FEBrick
    type_dict[vtk.VTK_PYRAMID] = ZoneType.FEBrick
    # Polytope
    type_dict[vtk.VTK_POLYGON] = ZoneType.FEPolygon
    type_dict[vtk.VTK_POLYHEDRON] = ZoneType.FEPolyhedron
    type_dict[vtk.VTK_CONVEX_POINT_SET] = ZoneType.FEPolyhedron
    type_dict[vtk.VTK_HEXAGONAL_PRISM] = ZoneType.FEPolyhedron
    return type_dict[vtk_cell_type]

def get_best_zone_type(vtk_cell_types):
    zone_types = set()
    for cell_type in vtk_cell_types:
        zone_types.add(zone_type(cell_type))
    final_zone_type = None
    # Select the most complex zone type
    if ZoneType.FEPolyhedron in zone_types:
        final_zone_type = ZoneType.FEPolyhedron
    elif ZoneType.FEBrick in zone_types:
        final_zone_type = ZoneType.FEBrick
    elif ZoneType.FETetra in zone_types:
        final_zone_type = ZoneType.FETetra
    elif ZoneType.FEPolygon in zone_types:
        final_zone_type = ZoneType.FEPolygon
    elif ZoneType.FEQuad in zone_types:
        final_zone_type = ZoneType.FEQuad
    elif ZoneType.FETriangle in zone_types:
        final_zone_type = ZoneType.FETriangle
    elif ZoneType.FELineSeg in zone_types:
        final_zone_type = ZoneType.FELineSeg
    return final_zone_type

def is_unstructured_zone(zone_type):
    return zone_type in [ZoneType.FEBrick,ZoneType.FELineSeg,ZoneType.FEQuad,ZoneType.FETetra,ZoneType.FETriangle]

def is_polytope_zone(zone_type):
     return zone_type in [ZoneType.FEPolygon,ZoneType.FEPolyhedron]

def get_points(output):
    """
    Returns a (3,n) array such that result[0] are the x-values, result[1] are y-values, result[2] are z-values
    """
    num_points = output.GetNumberOfPoints()
    points = np.empty((num_points,3))
    for i in range(num_points):
        # GetPoint returns a 3-value Tuple (x,y,z)
        points[i] = output.GetPoint(i)
    return points.transpose()

def get_dimensions(vtk_dataset):
    try:
        return vtk_dataset.GetDimensions()
    except TypeError:
        dims = [0, 0, 0]
        vtk_dataset.GetDimensions(dims)
        return tuple(dims)

def get_array_values(dims, arr, component):
    data = vtk.vtkDoubleArray()
    arr.GetData(0,arr.GetNumberOfTuples()-1,component,component,data)
    values = np.empty(dims)
    data.ExportToVoidPointer(values)
    return values.ravel()

def add_vtk_data(data, zone, location=ValueLocation.Nodal, name_counts=None):
    if name_counts is None:
        name_counts = dict()

    for i in range(data.GetNumberOfArrays()):
        arr = data.GetArray(i)
        if arr == None:
            print("Skipping empty array")
            continue
        vtk_type = arr.GetDataType()
        fd_type = field_data_type(vtk_type)
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            full_name = component_variable_name(name, num_components, component)
            occurrence = name_counts.get(full_name, 0)
            name_counts[full_name] = occurrence + 1

            variable = get_variable_by_occurrence(zone.dataset, full_name, occurrence)
            if variable is None:
                variable = add_variable(zone.dataset, full_name, fd_type, location)

            if location == ValueLocation.Nodal:
                values = get_array_values(zone.num_points, arr, component)
            else:
                # Value location is cell-centered
                values = get_array_values(zone.num_elements, arr, component)

                # Cell-centered values for 2D and 3D structured grids require padding in 360:
                if zone.zone_type == ZoneType.Ordered:
                    imax, jmax, kmax = zone.dimensions
                    if zone.rank == 3:
                        hpadding = np.zeros((kmax-1, jmax-1, 1)) 
                        vpadding = np.zeros((kmax-1,  1, imax)) 
                        values = values.reshape((kmax-1, jmax-1, imax-1))
                        values = np.concatenate((values,hpadding), axis=-1)
                        values = np.concatenate((values,vpadding), axis=1)
                    elif zone.rank == 2:
                        if kmax == 1:
                            hpadding = np.zeros((jmax-1, 1))
                            values = values.reshape((jmax-1, imax-1))
                        elif jmax == 1:
                            hpadding = np.zeros((kmax-1, 1))
                            values = values.reshape((kmax-1, imax-1))
                        else:  # imax == 1
                            hpadding = np.zeros((kmax-1, 1))
                            values = values.reshape((kmax-1, jmax-1))
 
                        values = np.concatenate((values,hpadding), axis=-1)
                    elif zone.rank == 1:
                        # I-ordered data is not padded in 360, so do not adjust.
                        pass
                    else: 
                        raise(f"rank of {zone} == {zone.rank}, not readable.")
                    values = values.ravel()
                    
            if fd_type in [FieldDataType.Float,FieldDataType.Double]:
                variable.values(zone)[:] = values
                    
            elif fd_type in [FieldDataType.Byte,FieldDataType.Int16]:
                variable.values(zone)[:] = values.astype(int)

def add_point_data(pd, zone, name_counts=None):
    add_vtk_data(pd, zone, location=ValueLocation.Nodal, name_counts=name_counts)

def add_cell_data(cd, zone, name_counts=None):
    add_vtk_data(cd, zone, location=ValueLocation.CellCentered, name_counts=name_counts)

def get_cell_connectivity(vtk_cell, zone_type):
    cell_type = vtk_cell.GetCellType()
    if cell_type in [vtk.VTK_QUADRATIC_TRIANGLE, vtk.VTK_QUADRATIC_TETRA]:
        idList = vtk.vtkIdList()
        triPoints = vtk.vtkPoints()
        vtk_cell.Triangulate(0, idList, triPoints)
        points = []
        for i in range(idList.GetNumberOfIds()):
            points.append(idList.GetId(i))

        def create_chunks(the_list, chunks):
            for i in range(0, len(the_list), chunks):
                yield the_list[i:i+chunks]
        num_nodes = dict()
        num_nodes[vtk.VTK_QUADRATIC_TRIANGLE] = 3
        num_nodes[vtk.VTK_QUADRATIC_TETRA] = 4
        chunked_points = create_chunks(points, num_nodes[cell_type])
        points = []
        for p in chunked_points:
            #
            # TODO: Need to come up with a generalized way to deal with collapsing cells when
            # a cell is added to a higher rank zone
            #
            if cell_type == vtk.VTK_QUADRATIC_TRIANGLE and zone_type == ZoneType.FETetra:
                assert(len(p) == 3)
                p = [p[0], p[1], p[2], p[2]]
            points.append(p)
    else:
        points = []
        for pt in range(vtk_cell.GetNumberOfPoints()):
            points.append(vtk_cell.GetPointId(pt))

    # Adapt the point IDs to work with Tecplot's need to have collapsed elements
    if zone_type == ZoneType.FEQuad and cell_type == vtk.VTK_TRIANGLE:
        assert(len(points) == 3)
        points = [points[0], points[1], points[2], points[2]]
    elif zone_type == ZoneType.FEBrick and cell_type == vtk.VTK_TETRA:
        # If we're adding Tetrahedrons to a "mixed element" zone we need to form them as collapsed bricks
        assert(len(points) == 4)
        points = [points[0], points[1], points[2], points[2], points[3], points[3], points[3], points[3]]
    elif cell_type == vtk.VTK_WEDGE:
        assert(zone_type == ZoneType.FEBrick)
        assert(len(points) == 6)
        points = [points[0], points[1], points[2], points[2], points[3], points[4], points[5], points[5]]
    elif cell_type == vtk.VTK_PYRAMID:
        assert(zone_type == ZoneType.FEBrick)
        assert(len(points) == 5)
        points = [points[0], points[1], points[2], points[3], points[4], points[4], points[4], points[4]]
    return points

def get_node_map(vtk_dataset, zone_type):
    # There has got to be a faster way to do this
    nodemap = []
    for i in range(vtk_dataset.GetNumberOfCells()):
        cell = vtk_dataset.GetCell(i)
        points = get_cell_connectivity(cell, zone_type)
        if isinstance(points[0], list):
            # We got a list of cells, which is what happens with high-order elements
            nodemap.extend(points)
        else:
            nodemap.append(points)
    return nodemap

def get_face_map(vtk_dataset, zone_type):
    ###
    ### face_map is a dictionary.
    ###   key = hash of sorted points
    ###   value = (points,left_cell,right_cell) # Three valued tuple.
    ###
    face_map = dict()
    for cell_number in range(vtk_dataset.GetNumberOfCells()):
        cell = vtk_dataset.GetCell(cell_number)
        num_faces = cell.GetNumberOfFaces() if zone_type == ZoneType.FEPolyhedron else cell.GetNumberOfEdges()
        for f in range(num_faces):
            face = cell.GetFace(f) if zone_type == ZoneType.FEPolyhedron else cell.GetEdge(f)
            points = []
            for pt in range(face.GetNumberOfPoints()):
                points.append(face.GetPointId(pt))
            pts = tuple(sorted(points))
            if pts not in face_map:
                face_map[pts] = (points, cell_number, -1)
            else:
                left_cell = face_map[pts][1]
                face_map[pts] = (points, left_cell, cell_number)
    return face_map

def add_connectivity_data(zone, node_map):
    assert(is_unstructured_zone(zone.zone_type))
    assert(len(node_map) == len(zone.nodemap))
    zone.nodemap[:] = node_map

def add_face_map(zone, face_map):
    assert(is_polytope_zone(zone.zone_type))
    assert(zone.num_faces == len(face_map))
    faces = []
    left_elements = []
    right_elements = []
    for v in face_map.values():
        points = v[0]
        faces.append(points)
        left_elements.append(v[1])
        right_elements.append(v[2])
    elements = (left_elements, right_elements)
    zone.facemap.set_mapping(faces, elements)

def add_unstructured_grid(vtk_dataset, tecplot_dataset, zone_name=DEFAULT_ZONE_NAME):
    assert(vtk_dataset)
    assert(vtk_dataset.GetDataObjectType() in [vtk.VTK_UNSTRUCTURED_GRID, vtk.VTK_POLY_DATA])

    num_cells = vtk_dataset.GetNumberOfCells()
    num_points = vtk_dataset.GetNumberOfPoints()
    print("Cells/Points: ", num_cells, num_points)
    if num_points == 0:
        return

    keyed_specs = prepare_vtk_dataset_variables(vtk_dataset, tecplot_dataset, include_cell_data=bool(num_cells))
    dtypes, locations = zone_variable_layout(tecplot_dataset, keyed_specs)

    if num_cells:
        cell_types = set()
        cell_type_array = vtk.vtkCellTypes()
        vtk_dataset.GetCellTypes(cell_type_array)
        for i in range(cell_type_array.GetNumberOfTypes()):
            cell_types.add(cell_type_array.GetCellType(i))
        if len(cell_types) > 1:
            print("Multiple cell types found: ", cell_types)
        zn_type = get_best_zone_type(cell_types)
        print("Chose ZoneType: ", zn_type)

        face_map = None
        node_map = None
        if is_unstructured_zone(zn_type):
            node_map = get_node_map(vtk_dataset, zn_type)
            #
            # For Quadratic data, we triangulate the cells so the node_map will report the
            # true number of cells
            #
            num_cells = len(node_map)
            zone = tecplot_dataset.add_fe_zone(zn_type, zone_name, num_points, num_cells,
                                               dtypes=dtypes, locations=locations)
        elif is_polytope_zone(zn_type):
            face_map = get_face_map(vtk_dataset, zn_type)
            zone = tecplot_dataset.add_poly_zone(zn_type, zone_name, num_points, num_cells,
                                                 len(face_map), dtypes=dtypes, locations=locations)
    else:
        # No Cells!
        assert(num_points >= 1)
        zone = tecplot_dataset.add_ordered_zone(zone_name, (num_points,1,1),
                                               dtypes=dtypes, locations=locations)

    # Write XYZ values
    xyz_points = get_points(vtk_dataset)
    zone.values(0)[:] = xyz_points[0]
    zone.values(1)[:] = xyz_points[1]
    zone.values(2)[:] = xyz_points[2]

    # TODO - Figure out how to use FieldData
    #fd = vtk_dataset.GetFieldData()

    name_counts = coordinate_name_counts(tecplot_dataset)
    pd = vtk_dataset.GetPointData()
    add_point_data(pd, zone, name_counts=name_counts)

    if num_cells:
        cd = vtk_dataset.GetCellData()
        add_cell_data(cd, zone, name_counts=name_counts)
        if is_polytope_zone(zone.zone_type):
            add_face_map(zone, face_map)
        else:
            add_connectivity_data(zone, node_map)
    return zone

def add_structured_grid(vtk_dataset, tecplot_dataset, zone_name=DEFAULT_ZONE_NAME):
    assert(vtk_dataset.GetDataObjectType() == vtk.VTK_STRUCTURED_GRID)

    dims = get_dimensions(vtk_dataset)
    keyed_specs = prepare_vtk_dataset_variables(vtk_dataset, tecplot_dataset)
    dtypes, locations = zone_variable_layout(tecplot_dataset, keyed_specs)
    zone = tecplot_dataset.add_ordered_zone(zone_name, dims, dtypes=dtypes, locations=locations)

    # Write XYZ values
    xyz_points = get_points(vtk_dataset)
    zone.values(0)[:] = xyz_points[0]
    zone.values(1)[:] = xyz_points[1]
    zone.values(2)[:] = xyz_points[2]

    # TODO - Figure out how to use FieldData
    #fd = vtk_dataset.GetFieldData()
    
    name_counts = coordinate_name_counts(tecplot_dataset)
    pd = vtk_dataset.GetPointData()
    add_point_data(pd, zone, name_counts=name_counts)

    cd = vtk_dataset.GetCellData()
    add_cell_data(cd, zone, name_counts=name_counts)

    return zone

def add_image_data(vtk_dataset, tecplot_dataset, zone_name=DEFAULT_ZONE_NAME):
    assert(vtk_dataset.GetDataObjectType() == vtk.VTK_IMAGE_DATA)

    dims = get_dimensions(vtk_dataset)
    pd = vtk_dataset.GetPointData()

    keyed_specs = prepare_image_data_variables(vtk_dataset, tecplot_dataset)
    dtypes, locations = zone_variable_layout(tecplot_dataset, keyed_specs)

    var_names = list(COORDINATE_VARIABLE_NAMES)
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        var_names.append(arr.GetName())

    zone = tecplot_dataset.add_ordered_zone(zone_name, dims, dtypes=dtypes, locations=locations)

    # Write XYZ values
    spacing = vtk_dataset.GetSpacing()
    bounds = vtk_dataset.GetBounds()
    xvals = np.linspace(bounds[0], bounds[1], dims[0])
    yvals = np.linspace(bounds[2], bounds[3], dims[1])
    zvals = np.linspace(bounds[4], bounds[5], dims[2])
    xx,yy,zz = np.meshgrid(xvals,yvals,zvals,indexing='ij')
    zone.values(0)[:] = xx.ravel()
    zone.values(1)[:] = yy.ravel()
    zone.values(2)[:] = zz.ravel()

    # Write the Point Data
    var_num = 3
    name_counts = coordinate_name_counts(tecplot_dataset)
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        vtk_type = arr.GetDataType()
        data = vtk.vtkDoubleArray()
        arr.GetData(0,arr.GetNumberOfTuples()-1,0,0,data)
        values = np.zeros(dims)
        data.ExportToVoidPointer(values)
        # VTI point data is not in the same IJK order as Tecplot, so we must
        # "roll" the values to reorder them.
        values = np.rollaxis(np.rollaxis(values,1), -1).ravel()
        fd_type = field_data_type(vtk_type)
        occurrence = name_counts.get(var_names[var_num], 0)
        name_counts[var_names[var_num]] = occurrence + 1
        variable = get_variable_by_occurrence(tecplot_dataset, var_names[var_num], occurrence)
        if variable is None:
            variable = add_variable(tecplot_dataset, var_names[var_num], fd_type,
                                    ValueLocation.Nodal)
        if fd_type == FieldDataType.Float or fd_type == FieldDataType.Double:
            variable.values(zone)[:] = values
        elif fd_type == FieldDataType.Byte or fd_type == FieldDataType.Int16:
            variable.values(zone)[:] = values.astype(int)
        var_num += 1

    return zone

def add_vtk_dataset(vtk_dataset, tecplot_dataset, zone_name=None):
    if vtk_dataset is None:
        return []
    if is_composite_dataset(vtk_dataset):
        return add_composite_dataset(vtk_dataset, tecplot_dataset, zone_name=zone_name)

    if zone_name is None:
        zone_name = DEFAULT_ZONE_NAME

    data_type = vtk_dataset.GetDataObjectType()
    if data_type in [vtk.VTK_UNSTRUCTURED_GRID, vtk.VTK_POLY_DATA]:
        zone = add_unstructured_grid(vtk_dataset, tecplot_dataset, zone_name=zone_name)
    elif data_type == vtk.VTK_STRUCTURED_GRID:
        zone = add_structured_grid(vtk_dataset, tecplot_dataset, zone_name=zone_name)
    elif data_type == vtk.VTK_IMAGE_DATA:
        zone = add_image_data(vtk_dataset, tecplot_dataset, zone_name=zone_name)
    else:
        print("Unrecognized DataType: ", data_type)
        return []

    if zone:
        return [zone]
    return []

def convert_vtk_file(vtk_file, plt_file, strand=None, solution_time=None):
    reader = get_vtk_reader(vtk_file)
    reader.SetFileName(vtk_file)
    reader.UpdateInformation()
    time_steps = reader_time_steps(reader)
    if solution_time is None and len(time_steps) == 1:
        solution_time = time_steps[0]
    reader.Update()
    vtk_dataset = reader.GetOutputDataObject(0)
    tp.new_layout()
    tecplot_dataset = tp.active_frame().dataset
    created_zones = add_vtk_dataset(vtk_dataset, tecplot_dataset)
    if tecplot_dataset.num_zones == 0:
        print("No zones created.")
        return
    if len(created_zones) == 1:
        created_zones[0].name = os.path.basename(vtk_file)
    else:
        for z in created_zones:
            if z.name == DEFAULT_ZONE_NAME:
                z.name = os.path.basename(vtk_file)
    for z in tecplot_dataset.zones():
        if strand is not None and solution_time is not None:
            z.strand = strand
            z.solution_time = solution_time
    tp.data.save_tecplot_plt(plt_file, dataset=tecplot_dataset)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert VTK/XDMF (.vtk, .vtu, .vtp, .vts, .vti, .vtkhdf, .hdf, .pdb, .xmf, .xdmf) files to Tecplot PLT format")
    parser.add_argument("infile", help="VTK file to convert")
    parser.add_argument("outfile", help="Name of Tecplot PLT (must end in .plt)")
    args = parser.parse_args()
    now = time.time()
    print("Converting: ", args.infile)
    convert_vtk_file(args.infile,args.outfile)
    print("File written to: ", args.outfile)
    print("Elapsed: ", time.time()-now)

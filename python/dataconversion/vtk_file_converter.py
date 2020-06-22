import sys
import os
import numpy as np
import vtk
import tecplot as tp
from tecplot.constant import *


def field_data_type(vtk_data_type):
    type_dict = dict()
    type_dict[vtk.VTK_BIT]           = FieldDataType.Bit
    type_dict[vtk.VTK_CHAR]          = FieldDataType.Byte 
    type_dict[vtk.VTK_UNSIGNED_CHAR] = FieldDataType.Byte
    type_dict[vtk.VTK_INT]           = FieldDataType.Int16
    type_dict[vtk.VTK_UNSIGNED_INT]  = FieldDataType.Int16
    type_dict[vtk.VTK_LONG]          = FieldDataType.Int32
    type_dict[vtk.VTK_UNSIGNED_LONG] = FieldDataType.Int32
    type_dict[vtk.VTK_FLOAT]         = FieldDataType.Float
    type_dict[vtk.VTK_DOUBLE]        = FieldDataType.Double
    return type_dict[vtk_data_type]

def zone_type(vtk_cell_type):
    type_dict = dict()
    type_dict[vtk.VTK_TRIANGLE] = ZoneType.FETriangle
    type_dict[vtk.VTK_QUAD]     = ZoneType.FEQuad 
    type_dict[vtk.VTK_TETRA]    = ZoneType.FETetra
    type_dict[vtk.VTK_HEXAHEDRON] = ZoneType.FEBrick
    # May need special code to create collapsed bricks
    type_dict[vtk.VTK_WEDGE] = ZoneType.FEBrick
    type_dict[vtk.VTK_PYRAMID] = ZoneType.FEBrick
    # Polytope
    type_dict[vtk.VTK_POLYGON] = ZoneType.FEPolygon
    type_dict[vtk.VTK_POLYHEDRON] = ZoneType.FEPolyhedron
    type_dict[vtk.VTK_CONVEX_POINT_SET] = ZoneType.FEPolyhedron
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

def get_array_values(dims, arr, component):
    data = vtk.vtkDoubleArray()
    arr.GetData(0,arr.GetNumberOfTuples()-1,component,component,data)
    values = np.empty(dims)
    data.ExportToVoidPointer(values)
    return values.ravel()

def add_vtk_data(data, zone, location=ValueLocation.Nodal):
    for i in range(data.GetNumberOfArrays()):
        arr = data.GetArray(i)
        type = arr.GetDataType()
        fd_type = field_data_type(type)
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            if num_components == 1:
                full_name = name
            else: 
                suffix = ['_X', '_Y', '_Z']
                full_name = name+suffix[component]
                
            variable = zone.dataset.add_variable(full_name, dtypes = [fd_type], locations=location)

            if location == ValueLocation.Nodal:
                values = get_array_values(zone.num_points, arr, component)
            else:
                values = get_array_values(zone.num_elements, arr, component)

            if fd_type in [FieldDataType.Float,FieldDataType.Double]:
                variable.values(zone)[:] = values
            elif fd_type in [FieldDataType.Byte,FieldDataType.Int16]:
                variable.values(zone)[:] = values.astype(int)

def add_point_data(pd, zone):
    add_vtk_data(pd, zone, location=ValueLocation.Nodal)
    
def add_cell_data(cd, zone):
    add_vtk_data(cd, zone, location=ValueLocation.CellCentered)

def get_node_map(vtk_dataset):
    # There has got to be a faster way to do this
    nodemap = []
    for i in range(vtk_dataset.GetNumberOfCells()):
        cell = vtk_dataset.GetCell(i)
        points = []
        for pt in range(cell.GetNumberOfPoints()):
            points.append(cell.GetPointId(pt))
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

def add_connectivity_data(vtk_dataset, zone):
    assert(is_unstructured_zone(zone.zone_type))
    nodemap = get_node_map(vtk_dataset)
    assert(len(nodemap) == len(zone.nodemap))
    zone.nodemap[:] = nodemap
    
def add_face_map(vtk_dataset, zone, face_map):
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

#def add_face_map_cell_based(vtk_dataset, zone, face_map):
#    assert(is_polytope_zone(zone.zone_type))
#    assert(zone.num_faces == len(face_map))
#    from tecplot.tecutil import _tecutil, lock
#    elementmap = []
#    for cell_number in range(vtk_dataset.GetNumberOfCells()):
#        cell = vtk_dataset.GetCell(cell_number)
#        num_faces = cell.GetNumberOfFaces()
#        element_faces = []
#        for f in range(num_faces):
#            face = cell.GetFace(f)
#            points = []
#            for pt in range(face.GetNumberOfPoints()):
#                points.append(face.GetPointId(pt))
#            element_faces.append(points)
#        elementmap.append(element_faces)
#    
#    nelems = len(elementmap)
#    faces_per_element = [len(e) for e in elementmap]
#    faces_per_element = (c_int32 * len(faces_per_element))(*faces_per_element)
#    nodes_per_face = [len(face) for elem in elementmap for face in elem]
#    nodes_per_face = (c_int32 * len(nodes_per_face))(*nodes_per_face)
#    elem_to_nodemap = [n+1 for elem in elementmap for face in elem for n in face]
#    elem_to_nodemap = (c_int32 * len(elem_to_nodemap))(*elem_to_nodemap)
#    with lock():
#        _tecutil.DataFaceMapAssignElemToNodeMap(zone.facemap, nelems, faces_per_element, nodes_per_face, elem_to_nodemap)
#    #zone.facemap.set_elementmap(tuple(elementmap))
    
def add_unstructured_grid(vtk_dataset, tecplot_dataset):
    assert(vtk_dataset)
    assert(vtk_dataset.GetDataObjectType() in [vtk.VTK_UNSTRUCTURED_GRID, vtk.VTK_POLY_DATA])
    
    num_cells = vtk_dataset.GetNumberOfCells()
    num_points = vtk_dataset.GetNumberOfPoints()
    
    if tecplot_dataset.num_variables == 0:
        # Add the XYZ variables - a dataset needs one variable before you can add a zone
        tecplot_dataset.add_variable('x', dtypes = [FieldDataType.Float])
        tecplot_dataset.add_variable('y', dtypes = [FieldDataType.Float])
        tecplot_dataset.add_variable('z', dtypes = [FieldDataType.Float])
        
    zone_name = "NO ZONE NAME"
    
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
        if is_unstructured_zone(zn_type):
            zone = tecplot_dataset.add_fe_zone(zn_type, zone_name, num_points, num_cells)
        elif is_polytope_zone(zn_type):
            face_map = get_face_map(vtk_dataset, zn_type)
            zone = tecplot_dataset.add_poly_zone(zn_type, zone_name, num_points, num_cells, len(face_map))
    else:
        # No Cells!
        zone = tecplot_dataset.add_ordered_zone(zone_name, (num_points,1,1))

    # Write XYZ values
    xyz_points = get_points(vtk_dataset)
    zone.values(0)[:] = xyz_points[0]
    zone.values(1)[:] = xyz_points[1]
    zone.values(2)[:] = xyz_points[2]
    
    # TODO - Figure out how to use FieldData
    #fd = vtk_dataset.GetFieldData()
    
    pd = vtk_dataset.GetPointData()
    add_point_data(pd, zone)
    
    if num_cells:
        cd = vtk_dataset.GetCellData()
        add_cell_data(cd, zone)
        if is_polytope_zone(zone.zone_type):
            add_face_map(vtk_dataset, zone, face_map)
        else:
            add_connectivity_data(vtk_dataset, zone)
    return zone

def add_structured_grid(vtk_dataset, tecplot_dataset):
    assert(vtk_dataset.GetDataObjectType() == vtk.VTK_STRUCTURED_GRID)

    if tecplot_dataset.num_variables == 0:
        # Add the XYZ variables - a dataset needs one variable before you can add a zone
        tecplot_dataset.add_variable('x', dtypes = [FieldDataType.Float])
        tecplot_dataset.add_variable('y', dtypes = [FieldDataType.Float])
        tecplot_dataset.add_variable('z', dtypes = [FieldDataType.Float])

    zone_name = "NO ZONE NAME"
    
    dims = vtk_dataset.GetDimensions()
    zone = tecplot_dataset.add_ordered_zone(zone_name, dims)

    # Write XYZ values
    xyz_points = get_points(vtk_dataset)
    zone.values(0)[:] = xyz_points[0]
    zone.values(1)[:] = xyz_points[1]
    zone.values(2)[:] = xyz_points[2]
    
    # TODO - Figure out how to use FieldData
    #fd = vtk_dataset.GetFieldData()
    
    pd = vtk_dataset.GetPointData()
    add_point_data(pd, zone)
    
    return zone

def add_image_data(vtk_dataset, tecplot_dataset):
    assert(vtk_dataset.GetDataObjectType() == vtk.VTK_IMAGE_DATA)

    dims = vtk_dataset.GetDimensions()
    pd = vtk_dataset.GetPointData()
    
    var_names = ['x', 'y', 'z']
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        var_names.append(arr.GetName())

    zone_name = "NO ZONE NAME"
    # Add the XYZ variables - a dataset needs one variable before you can add a zone
    tecplot_dataset.add_variable(var_names[0], dtypes = [FieldDataType.Float])
    tecplot_dataset.add_variable(var_names[1], dtypes = [FieldDataType.Float])
    tecplot_dataset.add_variable(var_names[2], dtypes = [FieldDataType.Float])
    zone = tecplot_dataset.add_ordered_zone(zone_name, dims)
    
    # Write XYZ values
    spacing = vtk_dataset.GetSpacing()
    origin = vtk_dataset.GetOrigin()
    xvals = np.linspace(origin[0] - spacing[0]*dims[0]/2, origin[0] + spacing[0]*dims[0]/2, dims[0])
    yvals = np.linspace(origin[1] - spacing[1]*dims[1]/2, origin[1] + spacing[1]*dims[1]/2, dims[1])
    zvals = np.linspace(origin[2] - spacing[2]*dims[2]/2, origin[2] + spacing[2]*dims[2]/2, dims[2])
    xx,yy,zz = np.meshgrid(xvals,yvals,zvals,indexing='ij')
    zone.values(0)[:] = xx.ravel()
    zone.values(1)[:] = yy.ravel()
    zone.values(2)[:] = zz.ravel()
    
    # Write the Point Data
    var_num = 3
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        type = arr.GetDataType()
        data = vtk.vtkDoubleArray()
        arr.GetData(0,arr.GetNumberOfTuples()-1,0,0,data)
        values = np.zeros(dims)
        data.ExportToVoidPointer(values)
        # VTI point data is not in the same IJK order as Tecplot, so we must
        # "roll" the values to reorder them.
        values = np.rollaxis(np.rollaxis(values,1), -1).ravel()
        fd_type = field_data_type(type)
        tecplot_dataset.add_variable(var_names[var_num], dtypes = [fd_type])
        if fd_type == FieldDataType.Float or fd_type == FieldDataType.Double:
            zone.values(var_num)[:] = values
        elif fd_type == FieldDataType.Byte or fd_type == FieldDataType.Int16:
            zone.values(var_num)[:] = values.astype(int)
        var_num += 1
    
    return zone
    

def add_vtk_dataset(vtk_dataset, tecplot_dataset):
    data_type = vtk_dataset.GetDataObjectType()
    if data_type in [vtk.VTK_UNSTRUCTURED_GRID, vtk.VTK_POLY_DATA]:
        add_unstructured_grid(vtk_dataset, tecplot_dataset)
    elif data_type == vtk.VTK_STRUCTURED_GRID:
        add_structured_grid(vtk_dataset, tecplot_dataset)
    elif data_type == vtk.VTK_IMAGE_DATA:
        add_image_data(vtk_dataset, tecplot_dataset)
        
def convert_vtk_file(vtk_file, plt_file):
    reader = None
    if vtk_file.endswith(".vtu"):
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif vtk_file.endswith(".vtp"):
        reader = vtk.vtkXMLPolyDataReader()
    elif vtk_file.endswith(".vts"):
        reader = vtk.vtkXMLStructuredGridReader()
    elif vtk_file.endswith(".vti"):
        reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(vtk_file)
    reader.Update()
    vtk_dataset = reader.GetOutput()
    tp.new_layout()
    tecplot_dataset = tp.active_frame().dataset
    add_vtk_dataset(vtk_dataset, tecplot_dataset)
    for z in tecplot_dataset.zones():
        z.name = os.path.basename(f)
    tp.data.save_tecplot_plt(plt_file, dataset=tecplot_dataset)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert VTK (.vtu, .vtp, .vts, .vti) files to Tecplot PLT format")
    parser.add_argument("infile", help="VTK file to convert")
    parser.add_argument("outfile", help="Name of Tecplot PLT (must end in .plt)")
    args = parser.parse_args()
    print("Converting: ", args.infile)
    convert_vtk_file(args.infile,args.outfile)
    print("File written to: ", args.outfile)


import ctypes
import numpy as np
import sys

tecio = ctypes.cdll.LoadLibrary(r"C:\Program Files\Tecplot\Tecplot 360 EX Beta\bin\tecio.dll")
def open_file(file_name, dataset_title, var_names, use_double_precision=False):
    tecio.tecini142.restype=ctypes.c_int32
    tecio.tecini142.argtypes=(
            ctypes.c_char_p, #Title
            ctypes.c_char_p, #Variables
            ctypes.c_char_p, #FName
            ctypes.c_char_p, #ScratchDir
            ctypes.POINTER(ctypes.c_int32), # FileFormat
            ctypes.POINTER(ctypes.c_int32), # FileType
            ctypes.POINTER(ctypes.c_int32), #Debug
            ctypes.POINTER(ctypes.c_int32)) #IsDouble

    is_szl = True if file_name.endswith(".szplt") else False

    varnamelist = ",".join(var_names)
    scratch_dir = r"."
    fileformat = ctypes.c_int32(1 if is_szl else 0) # 0=PLT, 1=SZL
    filetype = ctypes.c_int32(0) # 0=Grid&Solution, 1=Grid, 2=Solution
    debug = ctypes.c_int32(0) # 0=No, 1=Yes
    isdouble = ctypes.c_int32(1 if use_double_precision else 0) # 0=float, 1=double
    ret = tecio.tecini142(
            ctypes.c_char_p(bytes(dataset_title, encoding="UTF-8")),
            ctypes.c_char_p(bytes(varnamelist, encoding="UTF-8")),
            ctypes.c_char_p(bytes(file_name, encoding="UTF-8")),
            ctypes.c_char_p(bytes(scratch_dir, encoding="UTF-8")),
            ctypes.byref(fileformat),
            ctypes.byref(filetype),
            ctypes.byref(debug),
            ctypes.byref(isdouble)
            )
    if ret != 0:
        raise Exception("open_file Error")
    return ret


def close_file():
    tecio.tecend142.restype=ctypes.c_int32
    #tecio.tecend142.argtypes=(,)

    ret = tecio.tecend142()
    if ret != 0:
        raise Exception("close_file Error")
    return ret

def create_ordered_zone(zone_name, shape, solution_time, strand, var_sharing=None, passive_vars=None):
    tecio.teczne142.restype=ctypes.c_int32
    tecio.teczne142.argtypes=(
            ctypes.c_char_p, # ZoneTitle
            ctypes.POINTER(ctypes.c_int32), # ZoneType
            ctypes.POINTER(ctypes.c_int32), # IMax
            ctypes.POINTER(ctypes.c_int32), # JMax
            ctypes.POINTER(ctypes.c_int32), # KMax
            ctypes.POINTER(ctypes.c_int32), # ICellMax
            ctypes.POINTER(ctypes.c_int32), # JCellMax
            ctypes.POINTER(ctypes.c_int32), # KCellMax
            ctypes.POINTER(ctypes.c_double), # SolutionTime
            ctypes.POINTER(ctypes.c_int32), # StrandID
            ctypes.POINTER(ctypes.c_int32), # ParentZone
            ctypes.POINTER(ctypes.c_int32), # IsBlock
            ctypes.POINTER(ctypes.c_int32), # NumFaceConnections
            ctypes.POINTER(ctypes.c_int32), # FaceNeighborMode
            ctypes.POINTER(ctypes.c_int32), # TotalNumFaceNodes
            ctypes.POINTER(ctypes.c_int32), # NumConnectedBoundaryFaces
            ctypes.POINTER(ctypes.c_int32), # TotalNumBoundaryConnections
            ctypes.POINTER(ctypes.c_int32), # PassiveVarList
            ctypes.POINTER(ctypes.c_int32), # ValueLocation
            ctypes.POINTER(ctypes.c_int32), # ShareVarFromZone
            ctypes.POINTER(ctypes.c_int32)) # ShareConnectivityFromZone

    passive_var_list = None
    if passive_vars:
        passive_var_list = (ctypes.c_int32*len(passive_vars))(*passive_vars)
    var_share_list = None
    if var_sharing:
        var_share_list = (ctypes.c_int32*len(var_sharing))(*var_sharing)

    zone_type = ctypes.c_int32(0) # Ordered Zone
    imax = ctypes.c_int32(shape[0])
    jmax = ctypes.c_int32(shape[1])
    kmax = ctypes.c_int32(shape[2])
    parent_zone = ctypes.c_int32(0)
    ignored = ctypes.c_int32(0)
    block_format = ctypes.c_int32(1)
    num_face_connections = ctypes.c_int32(0)
    face_neighbor_mode = ctypes.c_int32(0)
    total_num_face_nodes = ctypes.c_int32(0)
    num_connected_boundary_faces = ctypes.c_int32(0)
    total_num_boundary_connections = ctypes.c_int32(0)

    ret = tecio.teczne142(
            ctypes.c_char_p(bytes(zone_name, encoding="UTF-8")),
            ctypes.byref(zone_type),
            ctypes.byref(imax),
            ctypes.byref(jmax),
            ctypes.byref(kmax),
            ctypes.byref(ignored),
            ctypes.byref(ignored),
            ctypes.byref(ignored),
            ctypes.byref(ctypes.c_double(solution_time)),
            ctypes.byref(ctypes.c_int32(strand)),
            ctypes.byref(parent_zone),
            ctypes.byref(block_format),
            ctypes.byref(num_face_connections),
            ctypes.byref(face_neighbor_mode),
            ctypes.byref(total_num_face_nodes), # only applies to poly data
            ctypes.byref(num_connected_boundary_faces), # only applies to poly data
            ctypes.byref(total_num_boundary_connections), # only applies to poly data
            passive_var_list,
            None, # Value Location - None indicates nodal data
            var_share_list,
            ctypes.byref(ctypes.c_int32(0))) #ShareConnectivityFromZone
    if ret != 0:
        raise Exception("create_ordered_zone Error")
    return ret


def __zone_write_double_values(values):
    values = np.asarray(values,dtype=np.float64)
    tecio.tecdat142.restype=ctypes.c_int32
    tecio.tecdat142.argtypes=(
            ctypes.POINTER(ctypes.c_int32), # NumPts
            ctypes.POINTER(ctypes.c_double), #values
            ctypes.POINTER(ctypes.c_int32)) #isdouble 

    isdouble = ctypes.c_int32(1)
    ret = tecio.tecdat142(
            ctypes.byref(ctypes.c_int32(len(values))),
            ctypes.cast(values.ctypes.data, ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(isdouble))
    if ret != 0:
        raise Exception("zone_write_double_values Error")

def __zone_write_float_values(values):
    values = np.asarray(values,dtype=np.float32)
    tecio.tecdat142.restype=ctypes.c_int32
    tecio.tecdat142.argtypes=(
            ctypes.POINTER(ctypes.c_int32), # NumPts
            ctypes.POINTER(ctypes.c_float), #values
            ctypes.POINTER(ctypes.c_int32)) #isdouble 

    isdouble = ctypes.c_int32(0)
    ret = tecio.tecdat142(
            ctypes.byref(ctypes.c_int32(values.size)),
            ctypes.cast(values.ctypes.data, ctypes.POINTER(ctypes.c_float)),
            ctypes.byref(isdouble))
    if ret != 0:
        raise Exception("zone_write_float_values Error")

def zone_write_values(values):
    values = np.asarray(values)
    if values.dtype == np.float64:
        return __zone_write_double_values(values)
    else:
        return __zone_write_float_values(values)


def test(file_name, use_double):
    open_file(file_name, "Title", ['x','y','c'], use_double)
    create_ordered_zone("Zone", (3,3,1), 0, 0)
    zone_write_values([1,2,3,1,2,3,1,2,3]) #xvals
    zone_write_values([1,1,1,2,2,2,3,3,3]) #yvals
    zone_write_values([1,2,3,4,5,6,7,8,9]) #cvals
    close_file()

if "--test" in sys.argv:
    test("test_double.plt", True)
    test("test_float.plt", False)
    test("test_double.szplt", True)
    test("test_float.szplt", False)

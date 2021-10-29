import ctypes
import sys

tecio = ctypes.cdll.LoadLibrary(r"C:\Program Files\Tecplot\Tecplot 360 EX Beta\bin\tecio.dll")

#Constants
VALUELOCATION_CELLCENTERED = 0
VALUELOCATION_NODECENTERED = 1

FILETYPE_GRIDANDSOLUTION = 0
FILETYPE_GRID = 1
FILETYPE_SOLUTION = 2

# var_data_types
FD_DOUBLE = 2
FD_FLOAT = 1
FD_INT32 = 3
FD_INT16 = 4
FD_UINT8 = 5

# Only SZL files are supported.  Use the ".szplt" extension
def open_file(file_name, dataset_title, var_names, 
    file_type=FILETYPE_GRIDANDSOLUTION,
    grid_file_handle=None):

    tecio.tecFileWriterOpen.restype=ctypes.c_int32
    tecio.tecFileWriterOpen.argtypes=(
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p))

    file_handle = ctypes.c_void_p()
    varnamelist = ",".join(var_names)
    filetype = ctypes.c_int32(file_type) # 0=Grid&Solution, 1=Grid, 2=Solution
    ret = tecio.tecFileWriterOpen(
            ctypes.c_char_p(bytes(file_name, encoding="UTF-8")),
            ctypes.c_char_p(bytes(dataset_title, encoding="UTF-8")),
            ctypes.c_char_p(bytes(varnamelist, encoding="UTF-8")),
            1, # SZL is required with this API
            filetype, # 0 == Grid & Solution
            0,
            grid_file_handle, # Grid file handle
            ctypes.byref(file_handle))
    if ret != 0:
        raise Exception("open_file Error")
    return file_handle


def close_file(file_handle):
    tecio.tecFileWriterClose.restype=ctypes.c_int32
    tecio.tecFileWriterClose.argtypes=(ctypes.POINTER(ctypes.c_void_p),)

    ret = tecio.tecFileWriterClose(ctypes.byref(file_handle))
    if ret != 0:
        raise Exception("close_file Error")


def create_ordered_zone(file_handle, zone_name, shape, 
    var_sharing=None,
    var_data_types=None,
    value_locations=None):

    tecio.tecZoneCreateIJK.restype=ctypes.c_int32
    tecio.tecZoneCreateIJK.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_char_p, #zoneTitle
            ctypes.c_int64,  # I,J,K
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.POINTER(ctypes.c_int32), #varTypes
            ctypes.POINTER(ctypes.c_int32), #shareVarFromZone
            ctypes.POINTER(ctypes.c_int32), #valueLocations
            ctypes.POINTER(ctypes.c_int32), #passiveVarList
            ctypes.c_int32, #shareFaceNeighborsFromZone
            ctypes.c_int64, #numFaceConnections
            ctypes.c_int32, #faceNeighborMode
            ctypes.POINTER(ctypes.c_int32)) #zone

    zone = ctypes.c_int32()
    #var_types = (ctypes.c_int32*len(some_list))(*some_list)
    var_share_list = None
    if var_sharing:
        var_share_list = (ctypes.c_int32*len(var_sharing))(*var_sharing)
    var_type_list = None
    if var_data_types:
        var_type_list = (ctypes.c_int32*len(var_data_types))(*var_data_types)
    value_location_list = None
    if value_locations:
        value_location_list = (ctypes.c_int32*len(value_locations))(*value_locations)

    ret = tecio.tecZoneCreateIJK(file_handle, 
        ctypes.c_char_p(bytes(zone_name,encoding="UTF-8")),
        shape[0],
        shape[1],
        shape[2],
        var_type_list, #varTypes
        var_share_list, #shareVarFromZone
        value_location_list, #valueLocations
        None, #passiveVarList
        0, #shareFaceNeighborsFromZone
        0, #numFaceConnections
        0, #faceNeighborMode
        ctypes.byref(zone))
    if ret != 0:
        raise Exception("create_ordered_zone Error")
    return zone

def zone_set_solution_time(file_handle, zone, strand=0, solution_time=0):
    tecio.tecZoneSetUnsteadyOptions.restype=ctypes.c_int32
    tecio.tecZoneSetUnsteadyOptions.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_double, #solutionTime
            ctypes.c_int32)  #strand

    ret = tecio.tecZoneSetUnsteadyOptions(file_handle, zone, solution_time, strand)
    if ret != 0:
        raise Exception("zone_set_solution_time Error")

def zone_write_double_values(file_handle, zone, var, values):
    tecio.tecZoneVarWriteDoubleValues.restype=ctypes.c_int32
    tecio.tecZoneVarWriteDoubleValues.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_int32,  #var
            ctypes.c_int32,  #partition
            ctypes.c_int64,  #count
            ctypes.POINTER(ctypes.c_double)) #values

    values_ptr = (ctypes.c_double*len(values))(*values)
    ret = tecio.tecZoneVarWriteDoubleValues(file_handle,
            zone,
            var,
            0,
            len(values),
            values_ptr)
    if ret != 0:
        raise Exception("zone_write_double_values Error")

def zone_write_float_values(file_handle, zone, var, values):
    tecio.tecZoneVarWriteFloatValues.restype=ctypes.c_int32
    tecio.tecZoneVarWriteFloatValues.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_int32,  #var
            ctypes.c_int32,  #partition
            ctypes.c_int64,  #count
            ctypes.POINTER(ctypes.c_float)) #values

    values_ptr = (ctypes.c_float*len(values))(*values)
    ret = tecio.tecZoneVarWriteFloatValues(file_handle,
            zone,
            var,
            0,
            len(values),
            values_ptr)
    if ret != 0:
        raise Exception("zone_write_float_values Error")

def zone_write_int32_values(file_handle, zone, var, values):
    tecio.tecZoneVarWriteInt32Values.restype=ctypes.c_int32
    tecio.tecZoneVarWriteInt32Values.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_int32,  #var
            ctypes.c_int32,  #partition
            ctypes.c_int64,  #count
            ctypes.POINTER(ctypes.c_int32)) #values

    values_ptr = (ctypes.c_int32*len(values))(*values)
    ret = tecio.tecZoneVarWriteInt32Values(file_handle,
            zone,
            var,
            0,
            len(values),
            values_ptr)
    if ret != 0:
        raise Exception("zone_write_int32_values Error")

def zone_write_int16_values(file_handle, zone, var, values):
    tecio.tecZoneVarWriteInt16Values.restype=ctypes.c_int32
    tecio.tecZoneVarWriteInt16Values.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_int32,  #var
            ctypes.c_int32,  #partition
            ctypes.c_int64,  #count
            ctypes.POINTER(ctypes.c_int16)) #values

    values_ptr = (ctypes.c_int16*len(values))(*values)
    ret = tecio.tecZoneVarWriteInt16Values(file_handle,
            zone,
            var,
            0,
            len(values),
            values_ptr)
    if ret != 0:
        raise Exception("zone_write_int16_values Error")

def zone_write_uint8_values(file_handle, zone, var, values):
    tecio.tecZoneVarWriteUInt8Values.restype=ctypes.c_int32
    tecio.tecZoneVarWriteUInt8Values.argtypes=(
            ctypes.c_void_p, #file_handle
            ctypes.c_int32,  #zone
            ctypes.c_int32,  #var
            ctypes.c_int32,  #partition
            ctypes.c_int64,  #count
            ctypes.POINTER(ctypes.c_uint8)) #values

    values_ptr = (ctypes.c_uint8*len(values))(*values)
    ret = tecio.tecZoneVarWriteUInt8Values(file_handle,
            zone,
            var,
            0,
            len(values),
            values_ptr)
    if ret != 0:
        raise Exception("zone_write_uint8_values Error")

def test():
    import numpy as np
    f = open_file("test.szplt", "Title", ['byte','short','long','float','double'])
    zone = create_ordered_zone(f, "Zone", (3,3,1), var_sharing=None, var_data_types=[FD_UINT8,FD_INT16,FD_INT32,FD_FLOAT,FD_DOUBLE])
    zone_write_uint8_values(f, zone, 1, [1,2,3,1,2,3,1,2,3]) #byte vals
    zone_write_int16_values(f, zone, 2, [1,1,1,2,2,2,3,3,3]) #short vals
    zone_write_int32_values(f, zone, 3, [1,2,3,4,5,6,7,8,9]) #long vals
    zone_write_float_values(f, zone, 4, np.linspace(0,1,9)) #float vals
    zone_write_double_values(f, zone, 5, np.linspace(1,2,9)) #double vals
    close_file(f)
    print("Wrote test.szplt")

def test_gridandsolution(grid_file, solution_file):
    grid_file_handle = open_file(grid_file, "Title", ['x','y'], file_type=FILETYPE_GRID)
    value_locations = [
        VALUELOCATION_NODECENTERED, # 'x'
        VALUELOCATION_NODECENTERED] # 'y'
    zone = create_ordered_zone(grid_file_handle, "Zone", (3,3,1), value_locations=value_locations, var_data_types=[FD_DOUBLE]*2)
    zone_set_solution_time(grid_file_handle, zone, strand=1)
    zone_write_double_values(grid_file_handle, zone, 1, [1,2,3,1,2,3,1,2,3]) #xvals
    zone_write_double_values(grid_file_handle, zone, 2, [1,1,1,2,2,2,3,3,3]) #yvals

    for t in [1,2,3]:
        outfile = "{}_{}".format(t, solution_file)
        solution_file_handle = open_file(outfile, "Title", ['c'], file_type=FILETYPE_SOLUTION, grid_file_handle=grid_file_handle)
        value_locations = [VALUELOCATION_CELLCENTERED] # 'c'
        zone = create_ordered_zone(solution_file_handle, "Zone", (3,3,1), value_locations=value_locations, var_data_types=[FD_DOUBLE])
        zone_set_solution_time(solution_file_handle, zone, strand=1, solution_time=t)
        zone_write_double_values(solution_file_handle, zone, 1, [t*1,t*2,t*3,t*4]) #cvals
        close_file(solution_file_handle)
    close_file(grid_file_handle)

def test_ordered_ijk(file_name, ijk_dim):
    import numpy as np
    var_names = ['x','y','z', 'c']
    file_handle = open_file(file_name, "Title", var_names)
    value_locations = [
        VALUELOCATION_NODECENTERED, # 'x'
        VALUELOCATION_NODECENTERED, # 'y'
        VALUELOCATION_NODECENTERED, # 'z'
        VALUELOCATION_CELLCENTERED] # 'c'
    var_data_types = [FD_FLOAT]*len(var_names)
    zone = create_ordered_zone(file_handle, "Zone", ijk_dim, value_locations=value_locations, var_data_types=var_data_types)

    x_ = np.linspace(0., ijk_dim[0], ijk_dim[0])
    y_ = np.linspace(0., ijk_dim[1], ijk_dim[1])
    z_ = np.linspace(0., ijk_dim[2], ijk_dim[2])
    x, y = np.meshgrid(x_, y_, indexing='xy')
    x = np.array([x]*ijk_dim[2])
    y = np.array([y]*ijk_dim[2])
    z = np.repeat(z_, ijk_dim[0]*ijk_dim[1])

    zone_write_float_values(file_handle, zone, 1, x.flatten())
    zone_write_float_values(file_handle, zone, 2, y.flatten())
    zone_write_float_values(file_handle, zone, 3, z.flatten())

    num_cells = 1
    for i in ijk_dim:
        if i == 1:
            continue
        num_cells *= i-1
    print(num_cells)
    zone_write_float_values(file_handle, zone, 4, np.linspace(0,1,num_cells))

    close_file(file_handle)

if "--testgridandsolution" in sys.argv:
    test_gridandsolution("grid.szplt", "solution.szplt")

if "--test" in sys.argv:
    test()

if "--testordered" in sys.argv:
    test_ordered_ijk("ij_ordered.szplt", (3,4,1))
    test_ordered_ijk("jk_ordered.szplt", (1,3,4))
    test_ordered_ijk("ijk_ordered.szplt", (3,4,5))
    test_ordered_ijk("ik_ordered.szplt", (3,1,5))

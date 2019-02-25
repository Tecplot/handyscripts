import ctypes
import sys

tecio = ctypes.cdll.LoadLibrary(r"C:\Program Files\Tecplot\Tecplot 360 EX Beta\bin\tecio.dll")

# Only SZL files are supported.  Use the ".szplt" extension
def open_file(file_name, dataset_title, var_names):
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
    ret = tecio.tecFileWriterOpen(
            ctypes.c_char_p(bytes(file_name, encoding="UTF-8")),
            ctypes.c_char_p(bytes(dataset_title, encoding="UTF-8")),
            ctypes.c_char_p(bytes(varnamelist, encoding="UTF-8")),
            1, # SZL is required with this API
            0, # 0 == Grid & Solution
            0,
            None, # Grid file handle
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

# var_data_types
FD_DOUBLE = 2
FD_FLOAT = 1
FD_INT32 = 3
FD_INT16 = 4
FD_UINT8 = 5

def create_ordered_zone(file_handle, title, shape, var_sharing=None, var_data_types=None):
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
    ret = tecio.tecZoneCreateIJK(file_handle, 
        ctypes.c_char_p(bytes(title,encoding="UTF-8")),
        shape[0],
        shape[1],
        shape[2],
        var_type_list, #varTypes
        var_share_list, #shareVarFromZone
        None, #valueLocations
        None, #passiveVarList
        0, #shareFaceNeighborsFromZone
        0, #numFaceConnections
        0, #faceNeighborMode
        ctypes.byref(zone))
    if ret != 0:
        raise Exception("create_ordered_zone Error")
    return zone

def zone_set_solution_time(file_handle, zone, solution_time, strand):
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
    zone = create_ordered_zone(f, "Zone", (3,3,1), None, [FD_UINT8,FD_INT16,FD_INT32,FD_FLOAT,FD_DOUBLE])
    zone_write_uint8_values(f, zone, 1, [1,2,3,1,2,3,1,2,3]) #byte vals
    zone_write_int16_values(f, zone, 2, [1,1,1,2,2,2,3,3,3]) #short vals
    zone_write_int32_values(f, zone, 3, [1,2,3,4,5,6,7,8,9]) #long vals
    zone_write_float_values(f, zone, 4, np.linspace(0,1,9)) #float vals
    zone_write_double_values(f, zone, 5, np.linspace(1,2,9)) #double vals
    close_file(f)
    print("Wrote test.szplt")

if "--test" in sys.argv:
    test()

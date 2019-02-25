import sys
import numpy as np
import time
import vtk
import tecio_szl as tecio_szl
import tecio

def field_data_type(vtk_data_type):
    type_dict = dict()
    type_dict[vtk.VTK_BIT]           = tecio_szl.FD_UINT8
    type_dict[vtk.VTK_CHAR]          = tecio_szl.FD_UINT8 
    type_dict[vtk.VTK_UNSIGNED_CHAR] = tecio_szl.FD_UINT8
    type_dict[vtk.VTK_INT]           = tecio_szl.FD_INT16
    type_dict[vtk.VTK_UNSIGNED_INT]  = tecio_szl.FD_INT16
    type_dict[vtk.VTK_LONG]          = tecio_szl.FD_INT32
    type_dict[vtk.VTK_UNSIGNED_LONG] = tecio_szl.FD_INT32
    type_dict[vtk.VTK_FLOAT]         = tecio_szl.FD_FLOAT
    type_dict[vtk.VTK_DOUBLE]        = tecio_szl.FD_DOUBLE
    return type_dict[vtk_data_type]

#
# This function will only create SZL files. This uses a newer TecIO API which
# allows specification of the data type.  This should result in slightly
# smaller files for data files which contain data types smaller than single precision.
#
def convert_vti_file_szl(src, dst):
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(src)
    reader.Update()
    output = reader.GetOutput()
    
    dims = output.GetDimensions()
    fd = output.GetFieldData()
    cd = output.GetCellData()
    pd = output.GetPointData()
    
    var_names = ['x', 'y', 'z']
    var_data_types = [tecio_szl.FD_FLOAT,tecio_szl.FD_FLOAT,tecio_szl.FD_FLOAT]
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        var_names.append(arr.GetName())
        var_data_types.append(field_data_type(arr.GetDataType()))

    f = tecio_szl.open_file(dst, src, var_names)
    zone = tecio_szl.create_ordered_zone(f, src, dims, None, var_data_types)

    # Future - use FieldData to get the solution time
    #solution_time = 1
    #strand = 1
    #tecio_szl.zone_set_solution_time(f, zone, solution_time, strand)
    
    # Write XYZ values
    spacing = output.GetSpacing()
    origin = output.GetOrigin()
    xvals = np.linspace(origin[0] - spacing[0]*dims[0]/2, origin[0] + spacing[0]*dims[0]/2, dims[0])
    yvals = np.linspace(origin[1] - spacing[1]*dims[1]/2, origin[1] + spacing[1]*dims[1]/2, dims[1])
    zvals = np.linspace(origin[2] - spacing[2]*dims[2]/2, origin[2] + spacing[2]*dims[2]/2, dims[2])
    xx,yy,zz = np.meshgrid(xvals,yvals,zvals,indexing='ij')
    tecio_szl.zone_write_float_values(f, zone, 1, xx.ravel())
    tecio_szl.zone_write_float_values(f, zone, 2, yy.ravel())
    tecio_szl.zone_write_float_values(f, zone, 3, zz.ravel())

    # Write the Point Data
    var_num = 4
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        print("Writing: ", arr.GetName())

        # Get the data values from the array
        data = vtk.vtkDoubleArray()
        arr.GetData(0,arr.GetNumberOfTuples()-1,0,0,data)
        values = np.zeros(dims)
        data.ExportToVoidPointer(values)
        # VTI point data is not in the same IJK order as Tecplot, so we must
        # "roll" the values to reorder them.
        values = np.rollaxis(np.rollaxis(values,1), -1).ravel()

        # Write the values to the file
        fd_type = field_data_type(arr.GetDataType())
        if fd_type == tecio_szl.FD_DOUBLE:
            tecio_szl.zone_write_double_values(f, zone, var_num, values)
        elif fd_type == tecio_szl.FD_FLOAT:
            tecio_szl.zone_write_float_values(f, zone, var_num, values.astype(np.float32))
        elif fd_type == tecio_szl.FD_INT16:
            tecio_szl.zone_write_int16_values(f, zone, var_num, values.astype(np.int16))
        elif fd_type == tecio_szl.FD_UINT8:
            tecio_szl.zone_write_uint8_values(f, zone, var_num, values.astype(np.uint8))
        var_num += 1
    tecio_szl.close_file(f)

#
# This function will create PLT or SZL files, based on the file extension
#
# All variables are written as Float (single-precision) or Double, based on
# the use_double variable.
#
def convert_vti_file(src,dst):
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(src)
    reader.Update()
    output = reader.GetOutput()
    
    dims = output.GetDimensions()
    fd = output.GetFieldData()
    cd = output.GetCellData()
    pd = output.GetPointData()
    
    var_names = ['x', 'y', 'z']
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        var_names.append(arr.GetName())

    use_double = False
    tecio.open_file(dst, src, var_names, use_double)
    solution_time = 0
    strand = 0
    tecio.create_ordered_zone(src, dims, solution_time, strand)

    # Write XYZ values
    spacing = output.GetSpacing()
    origin = output.GetOrigin()
    xvals = np.linspace(origin[0] - spacing[0]*dims[0]/2, origin[0] + spacing[0]*dims[0]/2, dims[0])
    yvals = np.linspace(origin[1] - spacing[1]*dims[1]/2, origin[1] + spacing[1]*dims[1]/2, dims[1])
    zvals = np.linspace(origin[2] - spacing[2]*dims[2]/2, origin[2] + spacing[2]*dims[2]/2, dims[2])
    xx,yy,zz = np.meshgrid(xvals,yvals,zvals,indexing='ij')
    tecio.zone_write_values(xx.ravel())
    tecio.zone_write_values(yy.ravel())
    tecio.zone_write_values(zz.ravel())
    
    # Write the Point Data
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        print("Writing: ", arr.GetName())

        # Get the data values from the array
        data = vtk.vtkDoubleArray()
        arr.GetData(0,arr.GetNumberOfTuples()-1,0,0,data)
        values = np.zeros(dims)
        data.ExportToVoidPointer(values)
        # VTI point data is not in the same IJK order as Tecplot, so we must
        # "roll" the values to reorder them.
        values = np.rollaxis(np.rollaxis(values,1), -1).ravel()
        tecio.zone_write_values(values)
    tecio.close_file()
    
infile = sys.argv[1]  # .vti file
outfile = sys.argv[2] # .szplt or .plt file

convert_vti_file(infile, outfile)
#convert_vti_file_szl(infile, outfile) # outfile must have .szplt extension


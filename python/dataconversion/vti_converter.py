import sys
import time
import numpy as np
import vtk
import tecplot as tp
from tecplot.constant import FieldDataType

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

def create_dataset(filename):
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filename)
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

    tp.new_layout()
    ds = tp.active_frame().create_dataset(filename)
    # Add the XYZ variables - a dataset needs one variable before you can add a zone
    ds.add_variable(var_names[0], dtypes = [FieldDataType.Float])
    ds.add_variable(var_names[1], dtypes = [FieldDataType.Float])
    ds.add_variable(var_names[2], dtypes = [FieldDataType.Float])
    solution_time = float(filename.split('_')[-1].split('.')[0])
    strand = 1
    zone = ds.add_ordered_zone(filename, dims)
    zone.solution_time = solution_time
    zone.strand = strand

    # Write XYZ values
    spacing = output.GetSpacing()
    origin = output.GetOrigin()
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
        print("Writing: ", arr.GetName())
        data = vtk.vtkDoubleArray()
        arr.GetData(0,arr.GetNumberOfTuples()-1,0,0,data)
        values = np.zeros(dims)
        data.ExportToVoidPointer(values)
        # VTI point data is not in the same IJK order as Tecplot, so we must
        # "roll" the values to reorder them.
        values = np.rollaxis(np.rollaxis(values,1), -1).ravel()
        fd_type = field_data_type(type)
        ds.add_variable(var_names[var_num], dtypes = [fd_type])
        if fd_type == FieldDataType.Float or fd_type == FieldDataType.Double:
            zone.values(var_num)[:] = values
        elif fd_type == FieldDataType.Byte or fd_type == FieldDataType.Int16:
            zone.values(var_num)[:] = values.astype(int)
        var_num += 1
    return ds



def convert_vti_file(src, dst):
    start = time.time()
    tp.new_layout()
    print("Converting: ", src)
    ds = create_dataset(src)
    if dst.endswith(".szplt"):
        tp.data.save_tecplot_szl(dst, dataset=ds)
    elif dst.endswith(".plt"):
        tp.data.save_tecplot_plt(dst, dataset=ds)
    else:
        print("Unregognized extension.  Saving to PLT format")
        tp.data.save_tecplot_plt(dst+".plt", dataset=ds)
    print("Elapsed Time: ", time.time()-start)


infile = sys.argv[1]  # Should be .vti extension
outfile = sys.argv[2] # Should be .szplt or .plt extension
convert_vti_file(infile, outfile)

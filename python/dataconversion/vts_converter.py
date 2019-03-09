import sys
import os
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

def add_point_data(pd, zone):
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        type = arr.GetDataType()
        fd_type = field_data_type(type)
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            if num_components == 1:
                full_name = name
            else: 
                suffix = ['-X', '-Y', '-Z']
                full_name = name+suffix[component]
                
            variable = zone.dataset.add_variable(full_name, dtypes = [fd_type])

            values = get_array_values(zone.dimensions, arr, component)

            if fd_type in [FieldDataType.Float,FieldDataType.Double]:
                variable.values(zone)[:] = values
            elif fd_type in [FieldDataType.Byte,FieldDataType.Int16]:
                variable.values(zone)[:] = values.astype(int)

def create_dataset(filename):
    reader = vtk.vtkXMLStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    output = reader.GetOutput()
    
    dims = output.GetDimensions()
    fd = output.GetFieldData()
    cd = output.GetCellData()
    pd = output.GetPointData()
    
    tp.new_layout()
    ds = tp.active_frame().create_dataset(name=os.path.basename(filename))

    # Add the XYZ variables - a dataset needs one variable before you can add a zone
    ds.add_variable('x', dtypes = [FieldDataType.Float])
    ds.add_variable('y', dtypes = [FieldDataType.Float])
    ds.add_variable('z', dtypes = [FieldDataType.Float])

    zone_name = os.path.basename(filename)
    zone = ds.add_ordered_zone(zone_name, dims)

    # Not sure how to get solution time from VTS files yet
    #solution_time = float(filename.split('_')[-1].split('.')[0])
    #strand = 1
    #zone.solution_time = solution_time
    #zone.strand = strand

    # Write XYZ values
    xyz_points = get_points(output)
    zone.values(0)[:] = xyz_points[0]
    zone.values(1)[:] = xyz_points[1]
    zone.values(2)[:] = xyz_points[2]
    
    add_point_data(pd, zone)

    return ds


def convert_vts_file(src, dst):
    start = time.time()
    print("Converting: ", src)
    with tp.session.suspend():
        ds = create_dataset(src)
        if dst.endswith(".szplt"):
            tp.data.save_tecplot_szl(dst, dataset=ds)
        elif dst.endswith(".plt"):
            tp.data.save_tecplot_plt(dst, dataset=ds)
        else:
            print("Unregognized extension.  Saving to PLT format")
            tp.data.save_tecplot_plt(dst+".plt", dataset=ds)
    print("Elapsed Time: ", time.time()-start)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert VTK .vts files to Tecplot format")
    parser.add_argument("infile", help="VTS file to convert")
    parser.add_argument("outfile", help="Name of Tecplot PLT or SZPLT output file")
    args = parser.parse_args()
    convert_vts_file(args.infile,args.outfile)


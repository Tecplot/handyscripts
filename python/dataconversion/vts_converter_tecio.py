import sys
import os
import time
import numpy as np
import vtk
import tecio

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

def add_point_data(pd, dims):
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        type = arr.GetDataType()
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            if num_components == 1:
                full_name = name
            else: 
                suffix = ['-X', '-Y', '-Z']
                full_name = name+suffix[component]
                
            values = get_array_values(dims, arr, component)
            tecio.zone_write_values(values)

def get_variable_names(pd):
    var_names = ['x','y','z']
    for i in range(pd.GetNumberOfArrays()):
        arr = pd.GetArray(i)
        name = arr.GetName()
        num_components = arr.GetNumberOfComponents()
        for component in range(num_components):
            if num_components == 1:
                full_name = name
            else: 
                suffix = ['-X', '-Y', '-Z']
                full_name = name+suffix[component]
            var_names.append(full_name)
    return var_names
                

def convert_vts_file(src, dst):
    start = time.time()
    reader = vtk.vtkXMLStructuredGridReader()
    reader.SetFileName(src)
    reader.Update()
    output = reader.GetOutput()
    
    dims = output.GetDimensions()
    fd = output.GetFieldData()
    cd = output.GetCellData()
    pd = output.GetPointData()
    
    var_names = get_variable_names(pd)
    use_double = False
    tecio.open_file(dst, src, var_names, use_double)
    # Not sure how to get solution time from VTS files yet
    solution_time = 0
    strand = 0
    tecio.create_ordered_zone(src, dims, solution_time, strand)

    # Write XYZ values
    xyz_points = get_points(output)
    tecio.zone_write_values(xyz_points[0])
    tecio.zone_write_values(xyz_points[1])
    tecio.zone_write_values(xyz_points[2])
    
    add_point_data(pd, dims)
    print("Elapsed Time: ", time.time()-start)
    tecio.close_file()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert VTK .vts files to Tecplot format")
    parser.add_argument("infile", help="VTS file to convert")
    parser.add_argument("outfile", help="Name of Tecplot PLT or SZPLT output file")
    args = parser.parse_args()
    convert_vts_file(args.infile,args.outfile)


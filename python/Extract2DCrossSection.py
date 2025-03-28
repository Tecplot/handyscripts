"""
Script that gives user ability to create a 2D cross-section
or "transect" from a defined polyline zone in Tecplot.

Usage:
Default behavior searches for a zone titled "Extracted Points" in given dataset. 
The variables assigned to x,y, and z-axes are used for computation of distance. 


A slice zone is created for each line segment of given polyline.
The slice is then blanked to fit the polyline segment and extracted.
Slice zone distance is calculated using previous distance and pythagorean theorem.
2D image of full transect is created and plotted.
"""

import numpy as np
import types
import math
import time
import tecplot as tp
from tecplot.constant import *
tp.session.connect()
ds = tp.active_frame().dataset
plot = tp.active_frame().plot()


polyline_zone_name = "Extracted Points"


def setup_value_blanking(x1,y1,x2,y2):
    plot = tp.active_frame().plot()
    
    blanking = plot.value_blanking
    blanking.cell_mode = ValueBlankCellMode.AllCorners
    
    blanking.constraint(0).variable = ds.variable(x_var) # X variable
    blanking.constraint(0).comparison_operator = RelOp.LessThan
    blanking.constraint(0).comparison_value = min(x1,x2)
    blanking.constraint(0).active = True
    
    blanking.constraint(1).variable = ds.variable(x_var) # X variable
    blanking.constraint(1).comparison_operator = RelOp.GreaterThan
    blanking.constraint(1).comparison_value = max(x1,x2)
    blanking.constraint(1).active = True
    
    blanking.constraint(2).variable = ds.variable(y_var) # Y variable
    blanking.constraint(2).comparison_operator = RelOp.LessThan
    blanking.constraint(2).comparison_value = min(y1,y2)
    blanking.constraint(2).active = True
    
    blanking.constraint(3).variable = ds.variable(y_var) # Y variable
    blanking.constraint(3).comparison_operator = RelOp.GreaterThan
    blanking.constraint(3).comparison_value = max(y1,y2)
    blanking.constraint(3).active = True
    
    blanking.active = True


def compute_normal(x1,y1,x2,y2):
    # This code generated by ChatGPT
    P1 = np.array([x1, y1])
    P2 = np.array([x2, y2])

    # Compute the vector between the two points
    v = P2 - P1

    # Compute the normal vector (rotate 90 degrees)
    normal_vector = np.array([-v[1], v[0]])

    # Compute the magnitude of the normal vector
    magnitude = np.linalg.norm(normal_vector)

    # Normalize the normal vector to get the unit normal
    unit_normal = normal_vector / magnitude

    # Output the unit normal
    return unit_normal


def normals_are_similar(n1, n2):
    condition = math.isclose(n1[0], n2[0], abs_tol=1e-1) and math.isclose(n1[1], n2[1], abs_tol=1e-1)    
    if condition:
        return 1
    return -1


def extract_slice_segment(x1,y1,x2,y2,distance_offset):
    normal = compute_normal(x1,y1,x2,y2)
    setup_value_blanking(x1,y1,x2,y2)

    slice_zone = tp.data.extract.extract_slice(origin=(x1,y1,0),
                                               normal=(normal[0], normal[1], 0), 
                                               transient_mode=TransientOperationMode.AllSolutionTimes)
    
    # There may be multiple solution times, 
    # so we check for SliceGroup generator, instead of a zone.
    if type(slice_zone) == types.GeneratorType:
        multiple_slices = True
        all_slices = [i for i in slice_zone]
        slice_zone = all_slices[0]
    else:
        multiple_slices = False
    
    xvals = slice_zone.values(x_var)[:]
    yvals = slice_zone.values(y_var)[:]
    dd = np.sqrt((xvals - x1)**2 + (yvals - y1)**2)

    # Negate the distance if the point is "behind" the starting point
    nn = [normals_are_similar(normal, compute_normal(x1,y1,x,y)) for x,y in zip(xvals, yvals)]
    dd = dd*nn
    if multiple_slices:
        for slice in all_slices:
            slice.values('distance')[:] = dd + distance_offset    
    else:
        slice_zone.values('distance')[:] = dd + distance_offset
    tp.active_frame().plot().value_blanking.active = False 

    
with tp.session.suspend():
    start = time.time()
    if polyline_zone_name in [zone.name for zone in ds.zones()]:
        poly_zone = ds.zone(polyline_zone_name)
    else:
        print("\n")
        raise Exception(f"No zone found with the name '{polyline_zone_name}' ")
    
    x_var = plot.axes.x_axis.variable
    y_var = plot.axes.y_axis.variable
    z_var = plot.axes.z_axis.variable
    xvals = ds.zone(poly_zone).values(x_var)[:]
    yvals = ds.zone(poly_zone).values(y_var)[:]
    ds.add_variable('distance')
    cumulative_distance = 0
    print("Found polyline zone, extracting slices.")
    for i in range(len(xvals)-1):
        
        x1,y1 = xvals[i],yvals[i]
        x2,y2 = xvals[i+1], yvals[i+1]
        extract_slice_segment(x1,y1,x2,y2, cumulative_distance)
        poly_zone.values('distance')[i] = cumulative_distance
        cumulative_distance += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    print("Slices extracted, displaying vertical transect.")
    poly_zone.values('distance')[len(xvals)-1] = cumulative_distance

    tp.active_frame().plot_type=PlotType.Cartesian2D
    tp.active_frame().plot().fieldmaps(0).show=False
    tp.active_frame().plot().fieldmaps(1).show=False
    tp.active_frame().plot().axes.x_axis.variable_index = ds.variable('distance').index
    tp.active_frame().plot().axes.y_axis.variable_index=ds.variable(z_var).index

    tp.active_frame().plot().axes.axis_mode=AxisMode.Independent
    tp.active_frame().plot().axes.x_axis.min = 0
    tp.active_frame().plot().axes.x_axis.max = ds.variable('distance').max()
    tp.active_frame().plot().axes.y_axis.min = ds.variable(z_var).min()
    tp.active_frame().plot().axes.y_axis.max = ds.variable(z_var).max()
    tp.active_frame().plot().show_contour = True
    
    tp.active_frame().plot().show_mesh = True
    tp.active_frame().plot().value_blanking.active = False 
    tp.macro.execute_command('$!RedrawAll')


print("Time Elapsed:", round(time.time()-start, 3))



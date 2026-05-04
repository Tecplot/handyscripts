"""Creates STL files from currently active FE-triangle zones.

Description
-----------
This connected-mode script creates STL files from currently active FE-Triangle zones. One STL file per zone.
Exported files are indexed by zone number.
Prior to execution of this script:
    1. Before extracting iso-surfaces, in the 'Iso-Surface Details' dialog, under 'Definition' tab,
        set 'Surface Generation Method' to 'All Triangles'. 
    2. Extract the iso-surfaces (Data>Extract>Iso-Surfaces...)
    3. Make the desired STL fieldmap(s) the only active FE-Tri fieldmap(s) in the Zone Style dialog.


Usage:
    General:
        > python .\FE_to_STL.py

Necessary modules
-----------------
numpy-stl
    A library for working with STL files leveraging the power of numpy.

numpy
    A general-purpose array processing package.

python-utils
    A collection of Python functions not included in the base install.

"""
import numpy as np
import tecplot as tp
from tecplot.constant import ZoneType, PlotType
from stl import mesh
# ---------------------------------
tp.session.connect()
frame = tp.active_frame()
plot = frame.plot()
if frame.plot_type != PlotType.Cartesian3D:
    print("Error: Frame must be 3D plot type")
    exit()
xvar = plot.axes.x_axis.variable
yvar = plot.axes.y_axis.variable
zvar = plot.axes.z_axis.variable
# ---------------------------------
for currentFieldMap in plot.active_fieldmaps:
    for currentZone in currentFieldMap.zones:
        if currentZone.zone_type == ZoneType.FETriangle:
            xValues = currentZone.values(xvar)[:]
            yValues = currentZone.values(yvar)[:]
            zValues = currentZone.values(zvar)[:]
            vertices = np.column_stack((xValues, yValues, zValues))
            faces = np.array(currentZone.nodemap[:])
            # Create the mesh
            cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    cube.vectors[i][j] = vertices[f[j], :]
            filename = ("zone-{}.stl").format(currentZone.index+1)
            # Write the mesh to file
            print("Writing file   {} ...".format(filename))
            cube.save(filename)
print("\nDone.")

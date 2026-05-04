########################################################
#
#  This PyTecplot script extracts values in the volume by extracting a 2D slice
#  then extracting a line from the extracted slice. By doing this much of the grid
#  spacing is retained.
#
#  Command line input:
#    Model: "JSM" or "HLCRM"
#    List of files with .cgns, or tecplots formats .dat, .plt or .szplt
#
#  Output:
#     Tecplot ASCII (.dat) file extracted at defined X,Y location.
#     The output file will have all variables as the incoming file.
#
#  Notes:
#     Required numpy.
#     Assumes Z variable is the 3rd variable.
#
########################################################


import sys
import os
import numpy
import tecplot as tp


###################### INPUT ###########################
if len(sys.argv) > 2:
    model = sys.argv[1]
    files = sys.argv[2:]
else:
    raise Exception("Please supply filenames.")


# One based index for the Z variable
z_var_number = 3


if model == 'JSM':
    # Define the point at the surface of the wing to extract "up" from
    # Z-values were determined by probing on surface of jsm_case01_medium_v2.cgns
    surface_points = [[2707.51, -565.81, -157.54],
                      [2906.34, -1295.41, -101.87]]

    # Arbitrary large value to extract to in the Z direction
    z_max = 500

elif model == "HLCRM":
    # Define the point at the surface of the wing to extract "up" from
    # Z-values were determined by probing on surface of GridPro_HLCRM_structured_Medium.cgns
    surface_points = [[1475, 277.5, 201.65],
                      [1290, 277.5, 162.79],
                      [1521, 427, 169.29],
                      [1527, 443, 171.48],
                      [1495, 638, 235.79],
                      [1615, 638, 214.42]]
    # Arbitrary large value to extract to in the Z direction
    z_max = 600
else:
    raise Exception('Please select model as JSM or HLCRM')

########################################################


def load_by_extension(filename):
    # Load any file with .cgns, .dat, .plt or .szplt file extension
    # Note: Sample loaders are provided here and additional loaders
    #   can be added using macro language.

    basename, ext = os.path.splitext(filename)
    if ext == '.cgns':
        # Load file with CGNS loader
        ds = tp.data.load_cgns(filename)
    elif ext in ['.dat', '.plt']:
        # Load file with Tecplot loader
        ds = tp.data.load_tecplot(filename)
    elif ext == '.szplt':
        # Load file with Tecplot SZL loader
        ds = tp.data.load_tecplot_szl(filename)
    else:
        raise Exception('Not recognized data extension')
    return ds


def blanking(variable_number, minimum, maximum):
    # Pure PyTecplot APIs do not exist yet for Blanking, so we fall back to
    # using the equivalent macro command here.
    #
    # Set up blanking for a minimum and maximum for a specific variable
    # Variable number is one based index
    str = """
    $!BLANKING VALUE{{CONSTRAINT 1 {{VARA = {0}}}}}
    $!BLANKING VALUE{{CONSTRAINT 1 {{RELOP = GREATERTHAN}}}}
    $!BLANKING VALUE{{CONSTRAINT 1 {{VALUECUTOFF = {1}}}}}
    $!BLANKING VALUE{{CONSTRAINT 1 {{RELOP = LESSTHANOREQUAL}}}}
    $!BLANKING VALUE{{CONSTRAINT 1 {{INCLUDE = YES}}}}
    $!BLANKING VALUE{{INCLUDE = YES}}
    $!BLANKING VALUE{{CONSTRAINT 2 {{VARA = {0}}}}}
    $!BLANKING VALUE{{CONSTRAINT 2 {{RELOP = GREATERTHANOREQUAL}}}}
    $!BLANKING VALUE{{CONSTRAINT 2 {{VALUECUTOFF = {2}}}}}
    $!BLANKING VALUE{{CONSTRAINT 2 {{INCLUDE = YES}}}}
    """.format(variable_number, minimum, maximum)
    tp.macro.execute_command(str)


def order_zone_by_z(in_zn, dataset, z_var_number):
    # Setup a new zone with the same dimension as the FE Line zone
    out_zn = dataset.add_ordered_zone(in_zn.name, in_zn.num_points)
    # Convert to ordered zone
    z = in_zn.values(z_var_number - 1).as_numpy_array()
    ii = numpy.argsort(z)
    for v in ds.variables():
        out_zn.values(v.index)[:] = in_zn.values(v.index).as_numpy_array()[ii]
    return out_zn


for fname in files:
    tp.new_layout()  # Reset between each file.

    # Accepts .dat, .plt, .cgns and .szplt
    ds = load_by_extension(fname)

    # Ensure that plot type is 3D cartesian
    tp.active_frame().plot_type = tp.constant.PlotType.Cartesian3D
    plot = tp.active_frame().plot()

    extracted_zones = []
    for locale in surface_points:

        # Extract to 2D slice from volume
        zn_2Dslice = tp.data.extract.extract_slice(origin=locale,
                                                   normal=(1, 0, 0),  # Slice along X direction
                                                   source=tp.constant.SliceSource.VolumeZones)

        # Ensure that only the extract slice is active at this point
        for fm in plot.fieldmaps():
            fm.show = False
        plot.fieldmap(zn_2Dslice).show = True

        # Using the surface values and a final (approximate) point to limit extraction extents
        blanking(z_var_number, locale[2], z_max)

        # Extract from only the extracted 2D slice a single 2D line
        zn_extract = tp.data.extract.extract_slice(origin=locale,
                                                   normal=(0, 1, 0),  # Slice along Y direction
                                                   source=tp.constant.SliceSource.SurfaceZones)

        # Convert the extracted FE zone to an I-Ordered zone, sorted by Z.
        ordered_extract = order_zone_by_z(zn_extract, ds, z_var_number)

        # Rename zone with filename and extraction position
        zn_name = os.path.splitext(fname)[0] + " x={x}, y={y}".format(x=locale[0], y=locale[1])
        ordered_extract.name = zn_name
        extracted_zones.append(ordered_extract)

        # Remove extraneous zone extractions (2D and un-ordered)
        ds.delete_zones([zn_2Dslice, zn_extract])

        # Turn the original data fieldmaps back on to ensure the extraction
        # goes through the appropriate zones
        for fm in plot.fieldmaps():
            fm.show = True
        plot.fieldmap(ordered_extract).show = False

    # Write out only extracted zones
    tp.data.save_tecplot_ascii(fname + '_velocity_profile.dat',
                               zones=extracted_zones,
                               use_point_format=True)

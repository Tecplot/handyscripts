########################################################
#
#  This PyTecplot script uses linear interpolation to extract values from volume
#  data to provided X,Y,Z locations (provided in HLCRM_velocity_extraction_points).
#
#  Command line input:
#     List of files with .cgns, or tecplots formats .dat, .plt or .szplt
#
#  Required Files:
#     HLCRM_velocity_extraction_points - Defines X,Y,Z locations for extraction.
#         Locations were extracted from the medium structured provided grid:
#         GridPro_HLCRM_structured_Medium.cgns
#
#  Output:
#     Tecplot ASCII (.dat) file of all non-grid variables interpolated to the
#         input X,Y,Z locations.
#
########################################################
import sys
import os
import tecplot as tp
from tecplot.constant import *


if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    raise Exception("Please supply filenames.")

# This file should be in the same directory as the PyTecplot script
interpolation_filename = r'HLCRM_velocity_extraction_points.dat'


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


for fname in files:
    tp.new_layout()
    ds = load_by_extension(fname)
    tp.active_frame.plot_type = PlotType.Cartesian3D
    orig_zones = ds.num_zones

    tp.data.load_tecplot(interpolation_filename)  # Zones are appended to orignial Dataset
    dest_zones = list(ds.zones())[orig_zones:]  # Get list of newly added zones

    # Linear interpolate only accepts volume zones into the source zone parameter.
    source_zones = [zn for zn in ds.zones() if zn.rank == 3]

    # Interpolate all non-grid variables to the velocity profile locations.
    for dest_zone in dest_zones:
        tp.data.operate.interpolate_linear(dest_zone, source_zones=source_zones)

    # Export extracted zones
    tp.data.save_tecplot_ascii(os.path.splitext(fname)[0] + '_velocity_profile.dat',
                               zones=dest_zones, use_point_format=True)

########################################################
#
#  This PyTecplot script extracts values from surface zones at given
#  slice locations defined by origin and normal. Slice locations in the
#  input section were extracted from HiLiftPW-3.JSM.SectionalCutter_v2.mcr
#  and HiLiftPW-3.HLCRM-SectionalCutter_v2.mcr for the two models.
#
#  Command line input:
#    Model: "JSM" or "HLCRM" or "OneraM6"
#    List of files with .cgns, or Tecplot formats .dat, .plt or .szplt
#    A sample file: Tecplot 360 EX/Examples/OneraM6wing/OneraM6_SU2_RANS.plt
#    Example: python -O sectional_extract.py JSM my_jsm_solution.cgns another_jsm_solution.szplt
#
#  Additional input:
#    Variable name: (lists) variables are matched by name. Add variable names
#      as exported by solvers used.
#    Sectional cuts: (dictionary) slice name, origin and normal
#      as defined in HiLiftPW-3.JSM.SectionalCutter_v2.mcr and
#      HiLiftPW-3.HLCRM-SectionalCutter_v2.mcr
#
#  Output:
#     Tecplot ASCII (.dat) file extracted at defined X,Y location.
#     The output file will have variables which match names given in
#       additonal input
#
########################################################

import sys
import os
import tecplot as tp

################# INPUT ###########################
if len(sys.argv) > 2:
    model = sys.argv[1]
    files = sys.argv[2:]
else:
    raise Exception("Please supply filenames.")

# Variable alias lists - update if your solver outputs different names
x_variable_names = ['x', 'CoordinateX']
y_variable_names = ['y', 'CoordinateY']
z_variable_names = ['z', 'CoordinateZ']
cp_variable_names = ['cp', 'Coefficient Pressure','Pressure Coefficient',
                     'C<sub>p</sub>', 'Pressure_Coefficient']
cf_variable_names = ['cf', 'Force Coefficient', 'Skin_Friction_Coefficient']
cfx_variable_names = ['cfx', 'Force Coefficient X']
cfy_variable_names = ['cfy', 'Force Coefficient Y']
cfz_variable_names = ['cfz', 'Force Coefficient Z']

variable_aliases = [x_variable_names, y_variable_names, z_variable_names, cp_variable_names,
             cf_variable_names, cfx_variable_names, cfy_variable_names, cfz_variable_names]

if model == 'JSM':
    # Python dict of section name, origin and normal (Taken from HiLiftPW-3.JSM.SectionalCutter_v2.mcr (updated 03/29/2017))
    sectional_cuts = {" slatA-A eta=0.16" :[[1.88529E+03, -3.93220E+02, -1.21820E+02],[0.041617, -0.979370, -0.197741]],
                      " wingA-A eta=0.16" :[[2.66397E+03, -3.68949E+02, -1.63180E+02],[0.000000, -0.998630,  0.052336]],
                      " flapA-A eta=0.16" :[[2.75207E+03, -3.74214E+02, -2.12251E+02],[0.022513,  0.997400, -0.068458]],
                      " slatB-B eta=0.25" :[[2.01323E+03, -5.88613E+02, -1.17578E+02],[0.041617, -0.979370, -0.197741]],
                      " wingB-B eta=0.25" :[[2.66443E+03, -5.63925E+02, -1.41428E+02],[0.000000, -0.998630,  0.052336]],
                      " flapB-B eta=0.25" :[[2.75376E+03, -5.69028E+02, -1.89207E+02],[0.022513,  0.997400, -0.068458]],
                      " wingC-C eta=0.33" :[[2.66488E+03, -7.58991E+02, -1.20093E+02],[0.000000, -0.998630,  0.052336]],
                      " flapC-C eta=0.33" :[[2.80467E+03, -7.68242E+02, -2.13068E+02],[0.022513,  0.997400, -0.068458]],
                      " slatD-D eta=0.41" :[[2.25561E+03, -9.59264E+02, -1.06694E+02],[0.055020, -0.976978, -0.206122]],
                      " wingD-D eta=0.41" :[[2.70351E+03, -9.34093E+02, -1.06152E+02],[0.000000, -0.998630,  0.052336]],
                      " flapD-D eta=0.41" :[[2.84134E+03, -9.54908E+02, -1.92803E+02],[0.029388, -0.956670,  0.289688]],
                      " slatE-E eta=0.56" :[[2.48536E+03, -1.31263E+03, -8.79189E+01],[0.055020, -0.976978, -0.206122]],
                      " wingE-E eta=0.56" :[[2.86617E+03, -1.28765E+03, -8.83407E+01],[0.000000, -0.998630,  0.052336]],
                      " flapE-E eta=0.56" :[[2.98732E+03, -1.31114E+03, -1.62036E+02],[0.029388, -0.956670,  0.289688]],
                      " slatG-G eta=0.77" :[[2.79930E+03, -1.79532E+03, -6.24533E+01],[0.055020, -0.976978, -0.206122]],
                      " wingG-G eta=0.77" :[[3.08838E+03, -1.77064E+03, -6.40080E+01],[0.000000, -0.998630,  0.052336]],
                      " flapG-G eta=0.77" :[[3.17849E+03, -1.77767E+03, -1.21743E+02],[0.029388, -0.956670,  0.289688]],
                      " slatH-H eta=0.89" :[[2.97876E+03, -2.07116E+03, -4.79897E+01],[0.055020, -0.976978, -0.206122]],
                      " wingH-H eta=0.89" :[[3.24813E+03, -2.04704E+03, -5.71650E+01],[0.000000, -0.998630,  0.052336]],
                      " fuselageN-N X=2504.88" :[[2.50488E+03, -4.59483E+01,  2.60586E+02],[1.000000,  0.000000,  0.000000]]}
elif model == 'HLCRM':
    # Python dict of section name, origin and normal (Taken from HiLiftPW-3.HLCRM.SectionalCutter_v2.mcr (updated 03/29/2017))
    sectional_cuts = {" eta=0.151, y=174.5" :[[0., 174.5, 0.],[ 0., 1., 0.]],
                      " eta=0.240, y=277.5" :[[0., 277.5, 0.],[ 0., 1., 0.]],
                      " eta=0.329, y=380.5" :[[0., 380.5, 0.],[ 0., 1., 0.]],
                      " eta=0.418, y=483.5" :[[0., 483.5, 0.],[ 0., 1., 0.]],
                      " eta=0.552, y=638"   :[[0., 638.0, 0.],[ 0., 1., 0.]],
                      " eta=0.685, y=792.5" :[[0., 792.5, 0.],[ 0., 1., 0.]],
                      " eta=0.819, y=947"   :[[0., 947.0, 0.],[ 0., 1., 0.]],
                      " eta=0.908, y=1050"  :[[0.,1050.0, 0.],[ 0., 1., 0.]]}
elif model == 'OneraM6':
    # Arbitrary cut locations for testing with the OneraM6 wing
    sectional_cuts = {" eta=0.151, y=0.20" :[[0., 0.20, 0.],[ 0., 1., 0.]],
                      " eta=0.240, y=0.44" :[[0., 0.44, 0.],[ 0., 1., 0.]],
                      " eta=0.329, y=0.65" :[[0., 0.65, 0.],[ 0., 1., 0.]],
                      " eta=0.418, y=0.80" :[[0., 0.80, 0.],[ 0., 1., 0.]]}
else:
    raise Exception('Please select model as JSM or HLCRM')
####################################################



def load_by_extension(filename):
    # Load any file with .cgns, .dat, .plt or .szplt file extension
    # Note: Sample loaders are provided here and additional loaders
    #   can be added using macro language.

    basename, ext = os.path.splitext(filename)
    if ext == '.cgns':
        # Load file with CGNS loader
        ds = tp.data.load_cgns(filename, include_boundary_conditions=True)
    elif ext in ['.dat', '.plt']:
        # Load file with Tecplot loader
        ds = tp.data.load_tecplot(filename)
    elif ext == '.szplt':
        # Load file with Tecplot SZL loader
        ds = tp.data.load_tecplot_szl(filename)
    else:
        raise Exception('Not recognized data extension')
    return ds



def variable_by_names(ds,variable_names):
    # Returns a PyTecplot variable object with name that matches any name in variable_names
    for var in ds.variables():
        if var.name in variable_names:
            return var
    return 'No variable found for: {0}'.format(str(variable_names))


for fname in files:
    tp.new_layout()
    basename = os.path.splitext(fname)[0]
    # Load file and ensure 3D plot type
    ds = load_by_extension(fname)
    tp.active_frame().plot_type = tp.constant.PlotType.Cartesian3D
    plot = tp.active_frame().plot()

    extracted_zones = []

    for sect_name in sectional_cuts.keys():
        location = sectional_cuts[sect_name]
        # Extract from surface at given origin and normal
        wing_cut = tp.data.extract.extract_slice(origin= location[0],
                                                 normal= location[1],
                                                 source= tp.constant.SliceSource.SurfaceZones)
        # Name extracted zone
        wing_cut.name = basename + sect_name
        extracted_zones.append(wing_cut)

    exported_variables = []
    # For variables, find variable objects to write out only those of interest
    for varnames in variable_aliases:
        var_obj=variable_by_names(ds, varnames)
        if isinstance(var_obj, tp.data.variable.Variable):
            exported_variables.append(var_obj)
        else:
            print(str(var_obj))

    tp.data.save_tecplot_ascii(basename + "_sectional.dat",
                               zones=extracted_zones,
                               variables=exported_variables,
                               use_point_format=True)

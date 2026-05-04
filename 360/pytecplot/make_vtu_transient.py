import re
import sys
import tecplot as tp

#
# Creates a transient PLT file from a VTU file in which the variables
# represent the time steps. Known variable naming conventions are COMSOL
# and SimVascular, which must be expressed on the command line.
#
# Usage:
#  make_vtu_transient.py <filename.vtu> [COMSOL|SimVascular]
#

with tp.session.suspend():
    vtu_file_name = sys.argv[1]
    plt_output_file = vtu_file_name + ".plt"

    if sys.argv[2] == "COMSOL":
        time_reg_ex = "_@_t=(.*)" # COMSOL
        time_value_group = 1
    elif: sys.argv[2] = "SimVascular"
        time_reg_ex = "_(\d+)" # SimVascular
        time_value_group = 1
    else:
        raise Exception("Unknown file format entered")

    tp.new_layout()
    tp.macro.execute_command("""$!ReadDataSet  '\"STANDARDSYNTAX\" \"1.0\" \"FILENAME_FILE\" \"%s\"'
      DataSetReader = 'VTK Data Loader'
      ReadDataOption = New
      ResetStyle = No
      AssignStrandIDs = Yes
      InitialPlotType = Automatic
      InitialPlotFirstZoneOnly = No
      AddZonesToExistingStrands = No
      VarLoadMode = ByName"""%(vtu_file_name))
    ds = tp.active_frame().dataset



    # Collect the transient variable names and their associated solution time values
    time_vars = dict()
    for v in ds.variables():
        try:
            res = re.search(time_reg_ex,v.name)
            if res:
                t = res.group(time_value_group)
                if t in time_vars:
                    time_vars[t].append(v)
                else:
                    time_vars[t] = [v]
        except:
            #Probably a non-transient variable
            print("Not processing: ", v.name)
            
    # Create one zone per soluiton time and copy the time variable
    # values into a single variable across solution times
    zones_to_delete = []
    vars_to_delete = []
    for z in ds.zones():
        zones_to_delete.append(z)
        for t,vars in time_vars.items():
            transient_zone = z.copy(share_variables=False) # XYZ will not be shared anymore.
            transient_zone.strand = 1
            transient_zone.solution_time = float(t)

            # Use Tecplot's equation syntax to copy the variable values to a "base" variable
            eqn = ""
            for v in vars:
                res = re.search(time_reg_ex,v.name)
                if not res:
                    raise Exception("Couldn't identify transient variable name")
                start,end = res.span()
                base_name = v.name[:start] + v.name[end:]
                vars_to_delete.append(v)
                eqn += "{%s} = {%s}\n"%(base_name, v.name)
            print(eqn)
            tp.data.operate.execute_equation(eqn, zones=[transient_zone])
    # Delete the original zones and variables
    ds.delete_zones(zones_to_delete)
    ds.delete_variables(vars_to_delete)

    # Reshare XYZ variables
    all_zones = list(ds.zones())
    vars_to_share = [ds.variable(0),ds.variable(1),ds.variable(2)]
    ds.share_variables(all_zones[0],all_zones[1:],vars_to_share)

    tp.data.save_tecplot_plt(plt_output_file,include_data_share_linkage=True)



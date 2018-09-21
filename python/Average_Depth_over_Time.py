import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

import numpy as np
import sys

def setup_zones(base_zone, offset, volume_zone): 
    """
    base_zone - surface zone to copy 
    offset - distance to move the copied surface
    volume_zone - source zone for interpolations
    return copied & interpolated zone
    """
    interp_zone = base_zone.copy(share_variables=False)
    eqn = '{{siglev}} = {{siglev}}+{}'.format(offset)
    #print(interp_zone.values('siglev')[0], eqn)
    tp.data.operate.execute_equation(equation=eqn,
        zones=[interp_zone])
    tp.data.operate.interpolate_linear(interp_zone, volume_zone, fill_value=0)
    return interp_zone


def avg_set_of_zones(source_zones, avg_zone, timestep):
    """
    source_zones - list of zones to average over. These zones should all have the same grid 
    avg_zone - zone to hold the averaged values. This again should have the same grid as source_zones
    timestep - volume zone to derrive time step info. 
    """
    avg_zone.name = timestep.name + ' Depth Averaged'
    avg_zone.strand = 88 # random number
    avg_zone.solution_time = timestep.solution_time

    # Add other variables that you don't want to average
    # This is case sensitive!!!
    variables_constant_through_time = ["x", "y", "lat", "lon"]

    equation = ""
    for v in tp.active_frame().dataset.variables():
        if v.name in variables_constant_through_time:
            continue
        equation = "{%s} = ("%(v.name)
        for z in source_zones:
            index = z.index+1 # Adding 1 because execute equation uses 1-based zone indices
            equation += "{%s}[%d] +"%(v.name, index)
        equation = equation[:-1]
        equation += ")/ %d"%(len(source_zones))
#        print(equation + "\n")
        tp.data.operate.execute_equation(equation, zones=[avg_zone])



# --------------------------------------------
#            Input Parameters
# datafile - Path to NetCFD FVCOM data file
# offsets - List of values to offset the base zone along the Z axis. 
#           For FVCOM these should be between -1,0 as they represent 
#           siglay values
# --------------------------------------------
        
if sys.argv:
    datafile = sys.argv[1] 
else: 
    datafile = r"C:\Users\devon\Tecplot, Inc\ProductMarketing - Documents\GeoSciences_Research\FVCOM_Demo\psm_0180.nc"

offsets = np.linspace(-1,0,num=10)


# --------------------------------------------
#    MAIN
# --------------------------------------------



# Comment the following line to connect to a running instance of Tecplot 360:
tp.session.connect()
with tp.session.suspend():
    # Setup dataset, plot and get list of original zones
    tp.new_layout()
    plot = tp.active_frame().plot()
    dataset = tp.data.load_fvcom(datafile)
    base_vol_zones = list(dataset.zones())
    
    # Switch to SigLev as Z variable and generate surface from SigLev isosurface = 0
    orig_z = plot.axes.z_axis.variable_index
    plot.axes.z_axis.variable = dataset.variable('siglev')
    plot.contour(0).variable = dataset.variable('siglev')
    plot.isosurface(0).isosurface_values[0] = 0
    tp.active_frame().plot(PlotType.Cartesian3D).show_isosurfaces=True
    tp.macro.execute_command('''$!ExtractIsoSurfaces 
      Group = 1
      ExtractMode = SingleZone''')
    base_zone = tp.active_frame().dataset.zone(-1)
    tp.active_frame().plot(PlotType.Cartesian3D).show_isosurfaces = False
    
            
    zones_to_delete = [base_zone] 

    # Loop though time
    for timestep in base_vol_zones: 
        cur_zones = []
        print(timestep.name)
        # Get volume values at given depth onto a common mesh. 
        for x in offsets:
            cur_zones.append(setup_zones(base_zone,x,timestep))
        
        # Calculate average of 
        avg_set_of_zones(cur_zones, base_zone.copy(), timestep)
        
        # Collate generated temp zones for deleation
        zones_to_delete.append(cur_zones)
        
    # Delete zones created for interpolation before averaging
    tp.active_frame().dataset.delete_zones(zones_to_delete)

    # Return back to Z
    plot.axes.z_axis.variable_index = orig_z 

# Save out data
tp.data.save_tecplot_plt('testout.plt')
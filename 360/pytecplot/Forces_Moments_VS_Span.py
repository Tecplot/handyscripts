import numpy as np
import os.path
import sys
import tecplot as tp
from tecplot.constant import Color, PlotType, SliceSource, SliceSurface, ValueLocation

'''
A set of functions to:
- calculate forces and moments (3 methods, for details see:
    https://kb.tecplot.com/2018/02/23/calculating-aerodynamic-forces-moments/)
- create and extract n surface slices in a given direction
- perform a scalar integration on a set of slices
- plots the integration results against the distance
'''

def calcForcesMoments(method, surface_zones, pressure, shear=["","",""], velocity=["","",""], dynamicVisc=""):
    """Computes forces and moments on a surface:
    - method: pressureOnly, pressureShear, pressureVelocity
    - pressure, shear, velocity, dynamicVisc: the field variables names
    - surface_zones: the surface zone(s) for the integration to be performed
    """

    #Computes the unit vector normal to the surface
    tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
        command="Calculate Function='GRIDKUNITNORMAL' Normalization='None'"\
            +" ValueLocation='CellCentered' CalculateOnDemand='F'"\
                +" UseMorePointsForFEGradientCalculations='F'")
        
    #Defines the string used in Tecplot's equations tool depending on the method
    eq = list()
    if method == "Pressure":
        eq += ['{px} = -{'+'{}'.format(pressure)+'}* {X Grid K Unit Normal}']
        eq += ['{py} = -{'+'{}'.format(pressure)+'}* {Y Grid K Unit Normal}']
        eq += ['{pz} = -{'+'{}'.format(pressure)+'}* {Z Grid K Unit Normal}']
        eq += ['{mx} = Y * {pz} - Z * {py}']
        eq += ['{my} = Z * {px} - X * {pz}']
        eq += ['{mz} = X * {py} - Y * {px}']
    elif method == "Pressure and Shear":
        eq += ['{taux} = {'+'{}'.format(shear[0])+'}- {X Grid K Unit Normal} *{'\
            +'{}'.format(pressure)+'}']
        eq += ['{tauy} = {'+'{}'.format(shear[1])+'}- {Y Grid K Unit Normal} *{'\
            +'{}'.format(pressure)+'}']
        eq += ['{tauz} = {'+'{}'.format(shear[2])+'}- {Z Grid K Unit Normal} *{'\
            +'{}'.format(pressure)+'}']
        eq += ['{mx} = Y * {tauz} - Z * {tauy}']
        eq += ['{my} = Z * {taux} - X * {tauz}']
        eq += ['{mz} = X * {tauy} - Y * {taux}']
    elif method == "Pressure and Velocity":
        tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
            command="Calculate Function='VELOCITYGRADIENT' Normalization='None'"\
                +" ValueLocation='Nodal' CalculateOnDemand='F'"\
                    +" UseMorePointsForFEGradientCalculations='F'")
        eq += ['{D} = {dUdX} + {dVdY} + {dWdZ}']
        eq += ['{T11} = {'+'{}'.format(dynamicVisc)+'} * (2 * {dUdX} - 2/3 * {D}) -{'\
            +'{}'.format(pressure)+'}']
        eq += ['{T12} = {'+'{}'.format(dynamicVisc)+'} * ({dVdX} + {dUdY})']
        eq += ['{T13} = {'+'{}'.format(dynamicVisc)+'} * ({dWdX} + {dUdZ})']
        eq += ['{T22} = {'+'{}'.format(dynamicVisc)+'} * (2 * {dVdY} - 2/3 * {D}) -{'\
            +'{}'.format(pressure)+'}']
        eq += ['{T23} = {'+'{}'.format(dynamicVisc)+'} * ({dVdZ} + {dWdY})']
        eq += ['{T33} = {'+'{}'.format(dynamicVisc)+'} * (2 * {dWdZ} - 2/3 * {D}) -{'\
            +'{}'.format(pressure)+'}']
        eq += ['{taux} = {T11} * {X Grid K Unit Normal} + {T12} * {Y Grid K Unit Normal}'\
            +' + {T13} * {Z Grid K Unit Normal}']
        eq += ['{tauy} = {T12} * {X Grid K Unit Normal} + {T22} * {Y Grid K Unit Normal}'\
            +' + {T23} * {Z Grid K Unit Normal}']
        eq += ['{tauz} = {T13} * {X Grid K Unit Normal} + {T23} * {Y Grid K Unit Normal}'\
            +' + {T33} * {Z Grid K Unit Normal}']
        eq += ['{mx} = Y * {tauz} - Z * {tauy}']
        eq += ['{my} = Z * {taux} - X * {tauz}']
        eq += ['{mz} = X * {tauy} - Y * {taux}']

    for e in eq: #do the computation only on the zone(s) of interest
        tp.data.operate.execute_equation(e,zones=surface_zones,value_location=ValueLocation.CellCentered)

def createSlices(numPts, direction, minPos, maxPos):
    """
    Defines and extracts numPts slices 
    equally spaced from min to max
    in the given direction
    """

    p=tp.active_frame().plot()
    ds = tp.active_frame().dataset

    p.show_slices=False
    sl=p.slice(0)
    sl.show_primary_slice=False
    sl.show_start_and_end_slices=True
    sl.slice_source=SliceSource.SurfaceZones

    if direction=="X":
        sl.orientation=SliceSurface.XPlanes
        sl.start_position=(minPos,0,0)
        sl.end_position=(maxPos,0,0)
    elif direction=="Y":
        sl.orientation=SliceSurface.YPlanes
        sl.start_position=(0,minPos,0)
        sl.end_position=(0,maxPos,0)
    elif direction=="Z":
        sl.orientation=SliceSurface.ZPlanes
        sl.start_position=(0,0,minPos)
        sl.end_position=(0,0,maxPos)
    else:
        print ("{} is not a valid direction (X,Y,Z) for the planes creation.".format(direction))
    sl.show_intermediate_slices=True
    sl.num_intermediate_slices=numPts-2

    #Extract the slices to zones
    sl.show=True
    
    sl.extract()
    slice_zones = list(ds.zones("Slice*")) # Get slice zones by name

    # This should work in PyTecplot 1.4+  and can replace the above 2 lines 
    # slice_zones = sl.extract()

    return slice_zones

def intForcesMoments(sliceZnes,method, direction):
    """
    Loops over the sliceZnes and performs an integration of Forces and moments
    for each slice (Scalar integrals, variables are depending on the method).
    Returns a ([dir, dirNormalized,fxNr,fyNr,fzNr,mxNr,myNr,mzNr]*Nslices array) 
    """
    #direction, norm_direction, fx,fy,fz,mx,my,mz
    forcesMoments=np.zeros((8,len(sliceZnes))) 
    
    ds = sliceZnes[0].dataset
    fr = ds.frame
    #Retrieves Forces and Moments variables
    xAxisNr=ds.variable(direction).index
    if method == "Pressure":
        fxNr=ds.variable('px').index
        fyNr=ds.variable('py').index
        fzNr=ds.variable('pz').index
    else:
        fxNr=ds.variable('taux').index
        fyNr=ds.variable('tauy').index
        fzNr=ds.variable('tauz').index
    mxNr=ds.variable('mx').index
    myNr=ds.variable('my').index
    mzNr=ds.variable('mz').index

    #Populates the returned array with the direction and integrated values
    for i,slice_zone in enumerate(sliceZnes):
        forcesMoments[(0,i)]= slice_zone.values(xAxisNr)[0]
        for j,var_index in enumerate([fxNr,fyNr,fzNr,mxNr,myNr,mzNr]):
            intCmde=("Integrate ["+"{}".format(slice_zone.index + 1)+"] VariableOption='Scalar'"\
                + " XOrigin=0 YOrigin=0 ZOrigin=0"\
                +" ScalarVar=" + "{}".format(var_index+1)\
                + " Absolute='F' ExcludeBlanked='F' XVariable=1 YVariable=2 ZVariable=3 "\
                + "IntegrateOver='Cells' IntegrateBy='Zones'"\
                + "IRange={MIN =1 MAX = 0 SKIP = 1}"\
                + " JRange={MIN =1 MAX = 0 SKIP = 1}"\
                + " KRange={MIN =1 MAX = 0 SKIP = 1}"\
                + " PlotResults='F' PlotAs='Result' TimeMin=0 TimeMax=0")
            tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
                command=intCmde)
            integrated_result = float(fr.aux_data['CFDA.INTEGRATION_TOTAL'])
            forcesMoments[(j+2,i)] = integrated_result
            slice_zone.aux_data[ds.variable(var_index).name] = integrated_result

    #Normalized direction:
    forcesMoments[1]=(forcesMoments[0]-forcesMoments[0].min())/(forcesMoments[0].max()-forcesMoments[0].min())

    return (forcesMoments)

def forcesMomentsVsSpan(forcesMoments, direction, normalized, newPage):
    """Performs the plot of Forces VS Span.
    Feel free to modify the plot type or load a stylesheet."""
    
    #Plot either on a new page or on a new frame
    if newPage == True:
        tp.add_page()
        tp.active_page().name='ForcesMomentsVsSpan'
        fr = tp.active_frame()
    else:
        fr  = tp.active_page().add_frame()
        tp.macro.execute_extended_command(command_processor_id='Multi Frame Manager',
            command='TILEFRAMESHORIZ')
    fr.name='ForcesMomentsVsSpan'

    #Creates a dataset to host the forces and moments matrix
    ds2 = fr.create_dataset('ForcesMomentsSpan',
        ['{}'.format(direction), 'Span in {} direction, normalized'.format(direction),
        'Fx','Fy','Fz', 'Mx', 'My', 'Mz'])
    zne=ds2.add_ordered_zone('Forces and Moments',(len(forcesMoments[0])))
    for v in range(8):
        zne.values(v)[:] = forcesMoments[v].ravel()

    #Defines the plot
    fr.plot_type=PlotType.XYLine
    p = fr.plot()

    #Delete existing linemaps
    nLm=range(p.num_linemaps)
    for lm in nLm:
        p.delete_linemaps(0)

    #Create linemaps for each force and moment component
    for lm in range(6):
        p.add_linemap()
        if normalized==False:
            p.linemap(lm).x_variable_index=0
        else:
            p.linemap(lm).x_variable_index=1
        p.linemap(lm).y_variable_index=lm+2
        p.linemap(lm).name='&DV&'
        p.linemap(lm).line.line_thickness=0.4
    p.linemap(2).y_axis_index=1 #Fz to be put on a second Y-axis
    for lm in range(3,6):       #Do not show moments by default
        p.linemap(lm).show=False
    p.linemap(0).line.color=Color.Custom31
    p.linemap(1).line.color=Color.Custom28
    p.linemap(2).line.color=Color.Custom29
    p.view.fit()

    #Legend and Axis setup
    p.legend.show = True
    p.legend.position = (80, 90)
    p.axes.y_axis(0).title.offset=9
    p.axes.y_axis(1).title.offset=9


'''
Main
This script illustrate how to use the functions defined in ForcesAndMoments.py
The dataset used is the ONERA M6 wing, that can be found in:
Tecplot's installation directory/examples/OneraM6wing
'''

#Slices Parameters:
nPts=200
direction="Y"
minPos=0.05
maxPos=1.15

#Integration parameters:
mode = "Pressure and Velocity"
#mode = "Pressure"
#mode = "Pressure and Shear"
pressure_var_name="Pressure"
sh=["Wall shear-1","Wall shear-2","Wall shear-3"]
dVi="SA Turbulent Eddy Viscosity" #"Turbulent Viscosity"

#ForcesVSSpan parameters
normalized=True
newPage=False

tp.session.connect()
#tp.macro.execute_command("$!LoadAddon 'tecutiltools_combinezones'")

#Loading the data
tp.new_layout()
examples_dir = tp.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
ds = tp.data.load_tecplot(datafile)
fr=tp.active_frame()


#setting the correct field variables
#
# TODO - Make sure that the variable numbers and variable names
#  are correct when doing Pressure and Velocity!!!
#  NOTE - the variable numbers here are 1-based
#
if mode == "Pressure and Velocity":
    tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
        command="SetFieldVariables ConvectionVarsAreMomentum='T'"\
            +" UVar=5 VVar=6 WVar=7 ID1='Pressure' Variable1=10 ID2='Density' Variable2=4")

#calculates the forces and moments, limit the calculation to the surface zones to save time
surface_zones = [z for z in ds.zones() if z.rank == 2]
calcForcesMoments(mode,surface_zones,pressure_var_name,shear=sh,dynamicVisc=dVi)

with tp.session.suspend():
    #Creating nPts slices along the wing
    slice_zones = createSlices(nPts,direction,minPos,maxPos)

with tp.session.suspend():
    #Integrates the forces and moments on each slice
    forcesMoments=intForcesMoments(slice_zones,mode,direction)

with tp.session.suspend():
    #Plots the forces and moments VS span
    forcesMomentsVsSpan(forcesMoments, direction, normalized, newPage)

#Delete the extracted slices
#ds.delete_zones(s)

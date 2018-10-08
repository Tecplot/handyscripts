import tecplot as tp
from tecplot.exception import *
from tecplot.constant import SliceSurface
tp.session.connect()

# contstraint_number is 0 based
def setup_blanking(frame, slice, constraint_number, variable):
    constraint_number += 1
    slice_blank_direction = "GreaterThanOrEqual"
    tp.macro.execute_command('$!Blanking Value{Include = Yes}')
    tp.macro.execute_command('$!Blanking Value{ValueBlankCellMode = AllCorners}')
    tp.macro.execute_command('$!Blanking Value{Constraint %d {Include = Yes}}'%(constraint_number))
    tp.macro.execute_command('$!Blanking Value{Constraint %d {VarA = "%s"}}'%(constraint_number, variable.name))
    tp.macro.execute_command('$!Blanking Value{Constraint %d {RelOp = %s}}'%(constraint_number, slice_blank_direction))
    tp.macro.execute_command('$!Blanking Value{Constraint %d {ValueCutoff = 0}}'%(constraint_number))


def calculate_plane_equation_from_slice(frame, slice):
    if slice.orientation == SliceSurface.XPlanes:
        n = [1,0,0]
    elif slice.orientation == SliceSurface.YPlanes:
        n = [0,1,0]
    elif slice.orientation == SliceSurface.ZPlanes:
        n = [0,0,1]
    elif slice.orientation == SliceSurface.Arbitrary:
        n = slice.arbitrary_normal
    else:
        raise TecplotTypeError("Slice must be X,Y,Z, or Arbitrary")
        
    o = slice.origin
    d = -(n[0]*o[0] + n[1]*o[1] + n[2]*o[2])
    var_name = "Slice%d_Blank"%(slice.index+1)
    equation = '{%s} = %f*x + %f*y + %f*z + %f'%(var_name,n[0], n[1], n[2],d)
    tp.data.operate.execute_equation(equation="%s"%(equation))
    return frame.dataset.variable(var_name)

frame = tp.active_frame()
slice_group = int(input("Which slice group? [1-8]" ))-1
slice = frame.plot().slice(slice_group)
var = calculate_plane_equation_from_slice(tp.active_frame(), slice)
setup_blanking(tp.active_frame(), slice, slice_group, var)


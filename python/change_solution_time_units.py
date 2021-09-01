"""Updating Solution Time to a running instance of Tecplot

Description
-----------
This connected-mode script (turn-on PyTecplot connections in the GUI) changes the solution time values
and stores the result as the new solution time or as zone aux data. The script runs an operator on a
specific number that is defined by the user, then outputs the value.
WARNING: the operator MUST be in quotes or using an escaped character.

Usage:
    General:
        > python change_solution_time_units.py [args]

    usage example:
        > python .\change_solution_time_units.py -o \* -n 2 -l auxdata
        > python .\change_solution_time_units.py --operation "/" --number 3600 --location solutiontime

Necessary modules
-----------------
datetime
    A module with generic date and time abilities.

operator
    A module with generic operation abilities. Allows operators to be used as a function.

"""

import datetime
import tecplot as tp
import operator
import argparse
parser = argparse.ArgumentParser(description="Provide arguments for the solution time.")
parser.add_argument("-o", "--operation", help="Operator used for solution time calculation. Must be escaped or in quotes.", choices=['+', '-', '*', '/'], type=str)
parser.add_argument("-n", "--number", help="Scalar number operated on solution time.", type=float)
parser.add_argument("-l", "--location", help="Location for solution time output. Either auxdata or solutiontime.", choices=['auxdata','solutiontime'], type=str)
args = parser.parse_args()

ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}

tp.session.connect()
with tp.session.suspend():
    for z in tp.active_frame().dataset.zones():
        if z.strand > 0:
            solution_time = z.solution_time
            number = args.number
            op_char = args.operation
            location = args.location
            op_func = ops[op_char]
            result = op_func(solution_time, number)
            
            # Two methods can be used:
            #   Add Zone Auxiliary Data with the new values. This doesn't modify the original data and
            #   has more flexibility since you can use string values. For example you want to format
            #   the string to represent hh:mm:ss format.
            if location == "auxdata":
                z.aux_data["SolutionTime"] = str(datetime.timedelta(seconds=result))
            
            #  Or you can modify the value in place. This is limited to numeric values.
            elif location == "solutiontime":
                z.solution_time = result
    #
    # If you added Zone Auxiliary Data, this will display the text (assuming FieldMap #1 has transient data).
    #
    if location == "auxdata":
        tp.active_frame().add_text("&(AUXZONE[ACTIVEOFFSET=1]:SolutionTime)", position=(50,50))

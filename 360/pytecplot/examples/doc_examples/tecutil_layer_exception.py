import tecplot as tp
from tecplot.tecutil import lock

'''
The following will print out something like:

    Assertion trap in function call from an Add-on:
    Assertion Type: Pre-condition
    Assertion: ArgListIsValid(ArgList)
    Tecplot version: 2018.3.0.92441
    Function: TecUtilStateChangedX
    Explanation: Argument list must be valid.
'''
try:
    with tp.tecutil.lock():
        tp.tecutil._tecutil.StateChangedX(None)
except tp.exception.TecplotError as e:
    print(e)

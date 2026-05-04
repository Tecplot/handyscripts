#!MC 1410
# A way to set auxzone data for all zones. Note, 
# equation will try to use AuxVarName in every zone.
# If AuxVarName does not exist in any zone, error is thrown.

$!VARSET |AuxVarName| = 'var name here'

$!Loop |NumZones|
$!AlterData  [|LOOP|]
  Equation = '{new} = AUXZONE[|LOOP|]:|AuxVarName|'
$!EndLoop
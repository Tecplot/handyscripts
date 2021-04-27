#!MC 1410
# For all zones, this macro automatically assigns the solution time of a zone as a variable of that same zone.
# For example, in the 1st iteration of the loop, if the 1st zone has a solution time of 0,
# then each value of solution_time in that 1st zone will be 0. For the 2nd iteration,
# if the solution time is 4.1e-05, then all solution_time values of zone 2 will be 4.1e-05.

$!Loop |NumZones|
$!AlterData  [|LOOP|]
  Equation = '{solution_time} = SOLUTIONTIME[|LOOP|]'
$!EndLoop


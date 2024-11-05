#!MC 1410
$!Varset |lowerBoundX| = 0.3
$!Varset |upperBoundX| = 0.6
$!Varset |lowerBoundY| = 0.4
$!Varset |upperBoundY| = 0.7

$!Blanking Value{Include = Yes}
$!Blanking Value{BlankEntireCell = No}
$!Blanking Value{ValueBlankCellMode = AllCorners}
# If you want more or less blanking these are the options:
# $!Blanking Value{ValueBlankCellMode = AnyCorner}
# $!Blanking Value{BlankEntireCell = Yes}



$!AlterData 
  IgnoreDivideByZero = Yes
  Equation = '{X_constraint} = IF(|lowerBoundX| > x || x > |upperBoundX|,  0, x)'
$!AlterData 
  IgnoreDivideByZero = Yes
  Equation = '{Y_constraint} = IF(|lowerBoundY| > y || y > |upperBoundY|,  0, x)'
$!AlterData 
  IgnoreDivideByZero = Yes
  Equation = '{full_constraint} = IF({X_constraint} > 0 && {Y_constraint} > 0, 1, 0)'

$!GETVARNUMBYNAME |constraintVar|
  NAME = "full_constraint"

$!Blanking Value{Constraint 1 {Include = Yes}}
$!Blanking Value{Constraint 1 {VarA = |constraintVar|}}
$!Blanking Value{Constraint 1 {RelOp = GreaterThan}}
$!Blanking Value{Constraint 1 {ValueCutoff = 0}}





$!View FitSurfaces
  ConsiderBlanking = Yes

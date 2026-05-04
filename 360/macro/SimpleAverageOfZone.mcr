#!MC 1410

# Creates a simple un-weighted arithmetic average of the specified variable
# in the specified zone.


$!VarSet |zone| = 1
$!VarSet |variable| = 3

$!GetFieldValueRefCount |NumPoints|
    Zone = |zone|
    Var = |variable|


$!VarSet |sum| = 0
$!Loop |NumPoints|
  $!GetFieldValue |value|
    Zone = |zone|
    Var = |variable|
    Index = |Loop|
  $!VarSet |sum| += |value|
$!EndLoop
$!VarSet |avg| = (|sum|/|NumPoints|)
$!Pause "Average is |avg|"

#!MC 1410

# Description:
# This script blanks line data for timesteps greater than the current time step
# so that the line appears to plot with time.
# This macro is to be applied on 3D CONVERGE data where .out files are also
# loaded in 2 separate XY Line plot frames. These 3 frames were tiled vertically
# where the top frame is titled "3D Data", the middle frame is titled
# "Line Data with Blanking", and the bottom frame is titled
# "Line Data with Marker". All of these frames are linked with time.
# A .mp4 animation is saved in the same location as this script.


$!Linking BetweenFrames{LinkSolutionTime = Yes}
$!PropagateLinking
  LinkType = BetweenFrames
  FrameCollection = All

$!FrameControl ActivateByName Name = "Line Data with Marker"
$!XYLineAxis XDetail 1 {MarkerGridline{Show = Yes}}

$!FrameControl ActivateByName Name = "Line Data with Blanking"
$!Blanking Value{Constraint 1 {RelOp = GreaterThan}}
$!Blanking Value{Constraint 1 {ValueCutoff = |SOLUTIONTIME|}}
$!Blanking Value{Constraint 1 {Include = Yes}}
$!Blanking Value{Include = Yes}
$!Blanking Value{Constraint 1 {VarB = 'Crank (DEG)'}}

$!ExportSetup ExportFormat = MPEG4
$!ExportSetup ImageWidth = 2048
$!ExportSetup ExportFName = "|MACROFILEPATH|/movie.mp4"
$!ExportStart

$!FrameControl ActivateByName Name = "3D Data"
$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
  COMMAND='QUERY.NUMTIMESTEPS NumTimeSteps'

$!Loop |NumTimeSteps|
  $!VarSet |TimeStep| = |Loop|
  $!FrameControl ActivateByName Name = "3D Data"
  $!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
    COMMAND='QUERY.TIMEATSTEP |TimeStep| CurTime'
  $!GlobalTime SolutionTime = |CurTime|

  $!FrameControl ActivateByName Name = "Line Data with Blanking"
  $!Blanking Value{Constraint 1 {ValueCutoff = |SOLUTIONTIME|}}
  $!ExportNextFrame
$!EndLoop
$!ExportFinish

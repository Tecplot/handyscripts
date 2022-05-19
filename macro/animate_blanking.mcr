#!MC 1410

# Description:
# This script blanks line data for timesteps greater than the current time step
# so that the line appears to plot with time.
#
# This macro opens the VortexShedding example data set from the 360 examples folder,
# applies the VortexShedding style sheet,
# creates a probe over time XY plot,
# updates the frame names,
# links the frames by solution time,
# applies blanking constraints to the XY line plot frame,
# and then exports a .mp4 movie in the same location as the script.


$!ReadDataSet  '"|TECHOME|/examples/SimpleData/VortexShedding.plt" '
$!ReadStyleSheet  "|TECHOME|/examples/SimpleData/VortexShedding.sty"
$!ExtendedCommand
  CommandProcessorID = 'Time Series Plot'
  Command = 'Command = CreatePlot StrandID = 1 XPos = 0.0029424973086 YPos = 0.00029341264924 ZPos = 0'

$!FrameControl ActivateByNumber
  Frame = 1
$!FrameName = 'Cartesian Plot'

$!FrameControl ActivateByNumber
  Frame = 2
$!FrameControl MoveToTopActive
$!FrameName = 'Line Data with Blanking'


$!Linking BetweenFrames{LinkSolutionTime = Yes}
$!PropagateLinking
  LinkType = BetweenFrames
  FrameCollection = All

$!FrameControl ActivateByName Name = "Line Data with Blanking"
$!XYLineAxis XDetail 1 {MarkerGridline{Show = No}}
$!Blanking Value{Constraint 1 {RelOp = GreaterThan}}
$!Blanking Value{Constraint 1 {ValueCutoff = |SOLUTIONTIME|}}
$!Blanking Value{Constraint 1 {Include = Yes}}
$!Blanking Value{Include = Yes}
$!Blanking Value{Constraint 1 {VarB = 'Solution Time'}}

$!ExportSetup ExportFormat = MPEG4
$!ExportSetup ImageWidth = 2048
$!ExportSetup ExportFName = "|MACROFILEPATH|/movie.mp4"
$!ExportStart

$!FrameControl ActivateByName Name = "Cartesian Plot"
$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
  COMMAND='QUERY.NUMTIMESTEPS NumTimeSteps'

$!Loop |NumTimeSteps|
  $!VarSet |TimeStep| = |Loop|
  $!FrameControl ActivateByName Name = "Cartesian Plot"
  $!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
    COMMAND='QUERY.TIMEATSTEP |TimeStep| CurTime'
  $!GlobalTime SolutionTime = |CurTime|

  $!FrameControl ActivateByName Name = "Line Data with Blanking"
  $!Blanking Value{Constraint 1 {ValueCutoff = |SOLUTIONTIME|}}
  $!ExportNextFrame
$!EndLoop

$!ExportFinish

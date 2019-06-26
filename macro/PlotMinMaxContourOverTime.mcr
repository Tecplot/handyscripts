#!MC 1410

#
# Get the variable name of the contour variable (limited to Contour Group #1)
#
$!EXTENDEDCOMMAND 
  COMMANDPROCESSORID='extendmcr'
  COMMAND='QUERY.VARNUMBYASSIGNMENT "C" ContourVarNum'
$!EXTENDEDCOMMAND 
  COMMANDPROCESSORID='extendmcr'
  COMMAND='QUERY.VARNAMEBYNUM |ContourVarNum| ContourVarName'

#
# Create a new zone that represents the MAXC value
# over time.  MAXC returns the maximum value of the
# variable which is assigned to Contour Group #1. See
# the scripting guide for more detail on MAXC.
#
$!EXTENDEDCOMMAND 
  COMMANDPROCESSORID='Extend Time MCR'
  COMMAND='QUERY.NUMTIMESTEPS NUMTIMESTEPS'

$!CREATERECTANGULARZONE 
  IMAX = |NUMTIMESTEPS|
  JMAX = 1
  KMAX = 1
  X1 = 0
  Y1 = 0
  Z1 = 0
  X2 = 1
  Y2 = 0
  Z2 = 0
$!VARSET |MaxContourZone| = |NUMZONES|
$!RENAMEDATASETZONE
  ZONE = |MaxContourZone|
  Name = "Max |ContourVarName| over Time"
  
$!CREATERECTANGULARZONE 
  IMAX = |NUMTIMESTEPS|
  JMAX = 1
  KMAX = 1
  X1 = 0
  Y1 = 0
  Z1 = 0
  X2 = 1
  Y2 = 0
  Z2 = 0
$!VARSET |MinContourZone| = |NUMZONES|
$!RENAMEDATASETZONE
  ZONE = |MinContourZone|
  Name = "Min |ContourVarName| over Time"

$!LOOP |NUMTIMESTEPS|
  $!EXTENDEDCOMMAND 
    COMMANDPROCESSORID='Extend Time MCR' 
    COMMAND='SET.CURTIMESTEP |LOOP|'
  $!EXTENDEDCOMMAND 
    COMMANDPROCESSORID='Extend Time MCR' 
    COMMAND='QUERY.TIMEATSTEP |LOOP| SolutionTime'

  # Instead of creating new variables, we just reuse variables
  # #1 and #2. This keeps the dataset a little cleaner, but if we
  # really wanted to create new variables we could do so using
  # the $!ALTERDATA command
  #
  # Variable #1 represents Solution Time
  $!SETFIELDVALUE
    ZONE = |MaxContourZone|
    VAR = 1
    INDEX = |LOOP|
    FIELDVALUE = |SolutionTime|
  $!SETFIELDVALUE
    ZONE = |MinContourZone|
    VAR = 1
    INDEX = |LOOP|
    FIELDVALUE = |SolutionTime|
  # Variable #2 represent the Max Contour Value
  $!SETFIELDVALUE
    ZONE = |MaxContourZone|
    VAR = 2
    INDEX = |LOOP|
    FIELDVALUE = |MAXC|
  $!SETFIELDVALUE
    ZONE = |MinContourZone|
    VAR = 2
    INDEX = |LOOP|
    FIELDVALUE = |MINC|
$!ENDLOOP

# We deactivate the zone we just created because we don't want it
# to display in the current plot.  We'll show it in a new frame instead.
$!ACTIVEFIELDZONES -= [|NUMZONES|]

# Turn on Time linking because we'll be turning on the
# Solution Time axis marker on the following XY frame and
# we want that marker to update as we animate over time.
$!LINKING BETWEENFRAMES {LINKSOLUTIONTIME = YES}

# Make sure the active frame is at the top of the frame stack.  This
# ensures that the new frame we create below will inherit this dataset
$!FRAMECONTROL MOVETOTOPACTIVE

#
# Now plot the new zone in an XY plot
#
$!CREATENEWFRAME 
  XYPOS
    {
    X = 1.3947
    Y = 4.6447
    }
  WIDTH = 8.1217
  HEIGHT = 3.2862
$!PLOTTYPE = XYLINE
$!DELETELINEMAPS 
$!CREATELINEMAP 
$!LINEMAP [1]  NAME = 'Max |ContourVarName| over Time'
$!LINEMAP [1]  ASSIGN{ZONE = |MaxContourZone|}
$!ACTIVELINEMAPS += [1]
$!VIEW FIT
$!XYLINEAXIS XDETAIL 1 {TITLE{TITLEMODE = USETEXT}}
$!XYLINEAXIS XDETAIL 1 {TITLE{TEXT = 'Solution Time'}}


$!CREATELINEMAP 
$!LINEMAP [2]  NAME = 'Min |ContourVarName| over Time'
$!LINEMAP [2]  ASSIGN{ZONE = |MinContourZone|}
$!LINEMAP [2]  ASSIGN{YAXIS = 2}
$!ACTIVELINEMAPS += [2]
$!VIEW FIT
$!XYLINEAXIS XDETAIL 1 {TITLE{TITLEMODE = USETEXT}}
$!XYLINEAXIS XDETAIL 1 {TITLE{TEXT = 'Solution Time'}}
$!XYLINEAXIS YDETAIL 1 {TITLE{TITLEMODE = USETEXT}}
$!XYLINEAXIS YDETAIL 1 {TITLE{TEXT = 'Max |ContourVarName| over Time'}}


# Show the solution time axis marker in the XY frame. We turn
# on solution time frame linking to ensure the line updates when
# we animate in the other frame.
$!LINKING BETWEENFRAMES {LINKSOLUTIONTIME = YES}
$!XYLINEAXIS XDETAIL 1 {MARKERGRIDLINE{SHOW = YES}}
$!XYLINEAXIS XDETAIL 1 {TITLE{TITLEMODE = USETEXT}}
$!XYLINEAXIS XDETAIL 1 {TITLE{TEXT = 'Solution Time'}}
$!XYLINEAXIS YDETAIL 2 {TITLE{TITLEMODE = USETEXT}}
$!XYLINEAXIS YDETAIL 2 {TITLE{TEXT = 'Min |ContourVarName| over Time'}}


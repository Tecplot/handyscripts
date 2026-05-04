#!MC 1410

#Perform a probing on a surface and retrieve the node and zone number
#Please make sure no Geometry or Polyline object is defined

#Node definition
$!PROMPTFORTEXTSTRING |nodenr|
	INSTRUCTIONS = "Node Number:"
$!PROMPTFORTEXTSTRING |zonenr|
	INSTRUCTIONS = "Zone Number:"
$!PROMPTFORTEXTSTRING |height|
	INSTRUCTIONS = "Distance to extract:"
$!PROMPTFORTEXTSTRING |vplot|
	INSTRUCTIONS = "Number of the variable to plot:"
#$!VARSET |vplot|=4 #uncomment for 4th variable as default
	
# if the {dist} variable already exists, delete it
$!GETVARNUMBYNAME |vname|
	NAME = "dist"
$!IF "|vname|" == "dist"
		$!DELETEVARS  [|vname|]
$!endif	

#if the grid unit normal vector hasn't beed calculated yet, compute it:
$!GETVARNUMBYNAME |xn|
	NAME = "X Grid K Unit Normal"
$!GETVARNUMBYNAME |yn|
	NAME = "Y Grid K Unit Normal"
$!GETVARNUMBYNAME |zn|
	NAME = "Z Grid K Unit Normal"
$!VARSET |varexists| = (|xn|*|yn|*|zn|) 
$!IF |varexists| == 0
	$!EXTENDEDCOMMAND 
	  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  COMMAND = 'Calculate Function=\'GRIDKUNITNORMAL\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'F\''
$!ENDIF

#Retrieves the normal vector components
$!GETVARNUMBYNAME |xn|
	NAME = "X Grid K Unit Normal"
$!GETVARNUMBYNAME |yn|
	NAME = "Y Grid K Unit Normal"
$!GETVARNUMBYNAME |zn|
	NAME = "Z Grid K Unit Normal"

#retrieves the position and the normal vector at the node of interest
$!GETFIELDVALUE |xval|
	ZONE = |zonenr|
	VAR = 1
	INDEX = |nodenr|
$!GETFIELDVALUE |yval|
	ZONE = |zonenr|
	VAR = 2
	INDEX = |nodenr|
$!GETFIELDVALUE |zval|
	ZONE = |zonenr|
	VAR = 3
	INDEX = |nodenr|
$!GETFIELDVALUE |xnorm|
	ZONE = |zonenr|
	VAR = |xn|
	INDEX = |nodenr|
$!GETFIELDVALUE |ynorm|
	ZONE = |zonenr|
	VAR = |yn|
	INDEX = |nodenr|
$!GETFIELDVALUE |znorm|
	ZONE = |zonenr|
	VAR = |zn|
	INDEX = |nodenr|

# coordinates of the last point of the geometry
$!VARSET |xvecend| = (|xval|+|xnorm|*|height|)
$!VARSET |yvecend| = (|yval|+|ynorm|*|height|)
$!VARSET |zvecend| = (|zval|+|znorm|*|height|)
	
#Define the geometry
#NB: the Grid3D argument passed to POSITIONCOORDSYS isn't available in the GUI
$!ATTACHGEOM 
	POSITIONCOORDSYS = Grid3D
	ANCHORPOS
		{
		X = 0
		Y = 0
		}
    RAWDATA
        1
        2
        |xval|	|yval|	|zval|
        |xvecend|	|yvecend|	|zvecend|


#select the geometry, extract a 100-points zone and delete the geometry
$!PICK ADDALL
    SELECTGEOMS = YES
$!EXTENDEDCOMMAND 
    COMMANDPROCESSORID = 'Extract Over Time'
    COMMAND = 'ExtractGeomOverTime:100'
$!PICK CLEAR

#Computes the distance along the line
$!ALTERDATA  [|NUMZONES|]
    EQUATION = '{dist}=(I-1)*(|height|/99)'
  
# Plot the profile in a new frame
$!CREATENEWFRAME 
    XYPOS
        {
        X = 2.7965
        Y = 1.0376
        }
    WIDTH = 4.6106
    HEIGHT = 4.2124
$!PLOTTYPE = XYLINE
$!DELETELINEMAPS 
$!CREATELINEMAP 
$!LINEMAP [1]  NAME = 'Profile extracted'
$!LINEMAP [1]  ASSIGN{XAXISVAR = |vplot|}
$!LINEMAP [1]  ASSIGN{YAXISVAR = |NUMVARS|}
$!LINEMAP [1]  ASSIGN{ZONE = |NUMZONES|}
$!ACTIVELINEMAPS += [1]
$!VIEW FIT
$!ATTACHTEXT 
    ANCHORPOS
        {
        X = 50.67178502879079
        Y = 81.5126050420168
        }
    TEXTSHAPE
        {
        ISBOLD = NO
        HEIGHT = 9
        }
    TEXT = 'x = |xval|\ny = |yval|\nz = |zval|\n'

#!MC 1410

#Let's calculate the tensor of velocity gradients (Analyze->Calculate Variable menu):
$!EXTENDEDCOMMAND 
	COMMANDPROCESSORID = 'CFDAnalyzer4'
	COMMAND = 'Calculate Function=\'VELOCITYGRADIENT\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'F\''
	
#Set of equations to define the S2+O2 decomposition of the tensor of velocity gradients
#Preliminary calculations
$!ALTERDATA EQUATION = '{s11} = {dUdX}'
$!ALTERDATA EQUATION = '{s12} = 0.5*({dUdY}+{dVdX})'
$!ALTERDATA EQUATION = '{s13} = 0.5*({dUdZ}+{dWdX})'
$!ALTERDATA EQUATION = '{s22} = {dVdY}'
$!ALTERDATA EQUATION = '{s23} = 0.5*({dVdZ}+{dWdY})'
$!ALTERDATA EQUATION = '{s33} = {dWdZ}'
$!ALTERDATA EQUATION = '{Omga12} = 0.5*({dUdY}-{dVdX})'
$!ALTERDATA EQUATION = '{Omga13} = 0.5*({dUdZ}-{dWdX})'
$!ALTERDATA EQUATION = '{Omga23} = 0.5*({dVdZ}-{dWdY})'

#S2+Ohm2 tensor
$!ALTERDATA EQUATION = '{s2o2_11} = {s11}**2 + {s12}**2 + {s13}**2 - {Omga12}**2 - {Omga13}**2'
$!ALTERDATA EQUATION = '{s2o2_12} = {s11}*{s12} + {s12}*{s22} + {s13}*{s23} - {Omga13}*{Omga23}'
$!ALTERDATA EQUATION = '{s2o2_13} = {s11}*{s13} + {s12}*{s23} + {s13}*{s33} - {Omga12}*{Omga23}'
$!ALTERDATA EQUATION = '{s2o2_22} = {s12}**2 + {s22}**2 + {s23}**2 - {Omga12}**2 - {Omga23}**2'
$!ALTERDATA EQUATION = '{s2o2_23} = {s12}*{s13} + {s22}*{s23} + {s23}*{s33} - {Omga12}*{Omga13}'
$!ALTERDATA EQUATION = '{s2o2_33} = {s13}**2 + {s23}**2 + {s33}**2 - {Omga13}**2 - {Omga23}**2'

#Let's retrieve the S2+O2 variables to be use by the tensor eigenvalues calculation tool
$!GETVARNUMBYNAME |numVars2o2_11|
	NAME = "s2o2_11"
$!GETVARNUMBYNAME |numVars2o2_12|
	NAME = "s2o2_12"
$!GETVARNUMBYNAME |numVars2o2_13|
	NAME = "s2o2_13"
$!GETVARNUMBYNAME |numVars2o2_22|
	NAME = "s2o2_22"
$!GETVARNUMBYNAME |numVars2o2_23|
	NAME = "s2o2_23"
$!GETVARNUMBYNAME |numVars2o2_33|
	NAME = "s2o2_33" 
	
#Tensor eigensystem (eigen-vectors and -values calculation)
$!EXTENDEDCOMMAND 
	COMMANDPROCESSORID = 'Tensor Eigensystem'
	COMMAND = 'T11VarNum = |numVars2o2_11|, T12VarNum = |numVars2o2_12|, T13VarNum = |numVars2o2_13|, T22VarNum = |numVars2o2_22|, T23VarNum = |numVars2o2_23|, T33VarNum = |numVars2o2_33|, SortEgnV = TRUE, SaveEgnVect = TRUE '

#!MC 1410
#Loops over time and extracts the vortex cores.

#Retrieve the number of time steps
$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
    COMMAND='QUERY.NUMTIMESTEPS NUMTIMESTEPS'

#Loops over time
$!LOOP |NUMTIMESTEPS|
	#Sets the time to the current step
	$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
		COMMAND='SET.CURTIMESTEP |LOOP|'
	#Extracts the vortex cores
	$!EXTENDEDCOMMAND 
		COMMANDPROCESSORID = 'CFDAnalyzer4'
		COMMAND = 'ExtractFlowFeature Feature=\'VortexCores\' VCoreMethod=\'Eigenmodes\' ResidenceTime=1 SolutionTime=1 ExcludeBlanked=\'F\''
$!ENDLOOP


#!MC 1410
#
#The CFD_analyser must know about field (convection) variables (menu Analyze->Field Variables)

#Let's calculate the tensor of velocity gradients (Analyze->Calculate Variable menu):
$!EXTENDEDCOMMAND 
	COMMANDPROCESSORID = 'CFDAnalyzer4'
	COMMAND = 'Calculate Function=\'VELOCITYGRADIENT\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'F\''

$!ALTERDATA EQUATION = '{P} = -({dUdX}+{dVdY}+{dWdZ})'#0 for incompressible flows
$!ALTERDATA EQUATION = '{Q} = (-{dUdY}*{dVdX}-{dUdZ}*{dWdX}-{dVdZ}*{dWdY}+{dUdX}*{dVdY}+{dWdZ}*{dUdX}+{dWdZ}*{dVdY})'
$!ALTERDATA EQUATION = '{R} = ({dUdX}*({dVdZ}*{dWdY}-{dVdY}*{dWdZ})+{dUdY}*({dVdX}*{dWdZ}-{dWdX}*{dVdZ})+{dUdZ}*({dWdX}*{dVdY}-{dVdx}*{dWdY}))'

$!ALTERDATA EQUATION = '{R2} = ({R}+(2/27)*{P}**3-{Q}*{P}/3)'
$!ALTERDATA EQUATION = '{Q2} = ({Q}-{P}**2/3)'

#Swirling Discriminant
#Determinant of the caracteristic equation:
$!ALTERDATA
  EQUATION = '{Delta} = ({Q2}/3)**3+({R2}/2)**2'

#Where Delta>=0, the tensor has one real eigen value and a conjugate pair of complex eigenvalues.
#We compute the solutions:
$!ALTERDATA EQUATION = '{Beta2} = IF ({Delta}>=0 ,(ABS(SQRT(ABS({Delta}))-{R2}/2))**(1/3),0)'
$!ALTERDATA EQUATION = '{Beta3} = IF ({Delta}>=0 ,(ABS(SQRT(ABS({Delta}))+{R2}/2))**(1/3),0)'

$!ALTERDATA EQUATION = '{LambdaCi}=(SQRT(3)/2)*({Beta2}+{Beta3})'
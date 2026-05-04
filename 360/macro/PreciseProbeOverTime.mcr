#!MC 1410
#Allows to probe over time by entering the X,Y,Z coordinates of the probe

$!PROMPTFORTEXTSTRING |xPosition| INSTRUCTIONS = "Enter X position of the probe."
$!PROMPTFORTEXTSTRING |yPosition| INSTRUCTIONS = "Enter Y position of the probe."
$!PROMPTFORTEXTSTRING |zPosition| INSTRUCTIONS = "Enter Z position of the probe."

$!EXTENDEDCOMMAND 
  COMMANDPROCESSORID = 'Time Series Plot'
  COMMAND = 'Command = CreatePlot StrandID = 1 XPos = |xPosition| YPos = |yPosition| ZPos = |zPosition|'


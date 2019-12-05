#!MC 1410

$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
	COMMAND='QUERY.NUMTIMESTEPS NUMTIMESTEPS'

$!AlterData
  Equation = '{Hours}=0'
$!AlterData
  Equation = '{Minutes}=0'
$!AlterData
  Equation = '{Seconds}=0'

$!LOOP |NUMTIMESTEPS|
	$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
		COMMAND='SET.CURTIMESTEP |LOOP|'
	$!EXTENDEDCOMMAND COMMANDPROCESSORID='extend time mcr'
		COMMAND='QUERY.TIMEATSTEP |LOOP| CURTIME'
	$!VARSET|SECONDS|=(frac(|CURTIME|/60)*60)
	$!VARSET|MINUTES|=(int(frac(|CURTIME|/3600)*60))
	$!VARSET|HOURS|=(int(|CURTIME|/3600))
	$!EXTENDEDCOMMAND COMMANDPROCESSORID='extendmcr'
		COMMAND='QUERY.ACTIVEZONES ZNUM'
	$!AlterData  [|ZNUM|]
	  Equation = '{Hours}=|HOURS|'
	$!AlterData  [|ZNUM|]
	  Equation = '{Minutes}=|MINUTES|'
	$!AlterData  [|ZNUM|]
	  Equation = '{Seconds}=|SECONDS|'
$!ENDLOOP

$!GETVARNUMBYNAME |numHours|
	NAME = "Hours"
$!GETVARNUMBYNAME |numMinutes|
	NAME = "Minutes"
$!GETVARNUMBYNAME |numSeconds|
	NAME = "Seconds"

$!AttachText 
  AnchorPos
    {
    X = 10
    Y = 90
    }
  TextShape
    {
    IsBold = No
    }
  Text = 'Time: &(MAXVAR[|numHours|])h:&(MAXVAR[|numMinutes|])m:&(MAXVAR[|numSeconds|]%.2f)s'
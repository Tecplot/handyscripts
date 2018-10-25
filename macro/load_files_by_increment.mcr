#!MC 1410

$!VarSet |numDigits| = ""
$!VarSet |FileBase| = ""
$!VarSet |increment| = ""
$!VarSet |numberoffiles| = ""

$!PROMPTFORTEXTSTRING |numDigits|
    INSTRUCTIONS = "Number of digits in filename"
$!PROMPTFORTEXTSTRING |FileBase|
    INSTRUCTIONS = "Base filename"
$!PROMPTFORTEXTSTRING |increment|
    INSTRUCTIONS = "Increment of file numbers"
$!PROMPTFORTEXTSTRING |numberoffiles|
    INSTRUCTIONS = "Number of total files"



$!LOOP |numberoffiles|
$!VARSET |add| = (|LOOP|*|increment|)
$!VARSET |n| = "|add|"

# format file numbers to correct digits

$!If |numDigits| == 0
   $!VarSet |finalN| = "|n|"
$!ElseIf |numDigits| == 1
   $!VarSet |finalN| = "|n|" # no use in formatting here
$!ElseIf |numDigits| == 2
  $!VarSet |finalN| = "|n%02d|"
$!ElseIf |numDigits| == 3
  $!VarSet |finalN| = "|n%03d|"
$!ElseIf |numDigits| == 4
  $!VarSet |finalN| = "|n%04d|"
$!ElseIf |numDigits| == 5
  $!VarSet |finalN| = "|n%05d|"
$!ElseIf |numDigits| == 6
  $!VarSet |finalN| = "|n%06d|"
$!Endif

$!PAUSE "|macrofilepath|/|FileBase||finalN|.plt"

#Checks to see if the file exists
$!EXTENDEDCOMMAND
COMMANDPROCESSORID = "extendmcr"
Command = 'QUERY.FILEEXISTS "|macrofilepath|/|FileBase||finalN|.plt" "exists"'
$!IF "|exists|" == "YES"
    $!READDATASET "|macrofilepath|/|FileBase||finalN|.plt"
      READDATAOPTION = APPEND 
$!ENDIF

$!ENDLOOP

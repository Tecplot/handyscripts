#!MC 1410
# USAGE: Uncomment the section you want to use.
# 1. Macro coding pattern for applying equation to most zones, but skipping every nth zone
# 2. Macro coding pattern for applying equation, but skipping some range of zones for every N zones. (generally N = #zones per timestep). 
# Ex: skip zones 4-6, within every 10 zones.


# -------------- 1 --------------
# input zone number n to skip.
# input equation inside loop.


#$!VARSET |n| = 22

#$!VARSET |TotalLoops| = (|NumZones| - (floor(|NumZones| / |n|)))
#$!Loop |TotalLoops|
#  $!IF (|LOOP| % |n|) != (0) 
#    $!AlterData  [|LOOP|]

#      Equation = '{newvarname} = your-equation'

#  $!ENDIF
#$!EndLoop



# -------------- 2 --------------
# input zone grouping number N. If you have 12 zones per timestep, then zones repeat, input 12
# input zone number M of the FIRST zone of the range you want to skip. I.e input 3 to skip zones 3, 3+1, ..., 3+(R-1)
# input number R of zones to to skip. I.e input 3 to skip zones M, M+1, M+2
# input equation inside loop.
# Ex: to skip zones 4-6, within every 10 zones, you'd input N=10, M=4, R=3
# Ex: to skip zone 9, within every 12 zones, you'd input N=12, M=9, R=0


#$!VARSET |N| = 22
#$!VARSET |M| = 3
#$!VARSET |R| = 3

#$!Loop |NumZones|
#  $!VARSET |ZoneGroup| = (floor(|LOOP| / |N|))
#  $!VARSET |RangeStart| = ( (|ZoneGroup|*|N|) + |M|-1)
#  $!VARSET |RangeFin| = ( (|ZoneGroup|*|N|) + |M|+|R|-1)
#  $!IF |LOOP| > (|RangeStart|) 
#    $!IF |LOOP| <= (|RangeFin|)
#      $!CONTINUE
#    $!ENDIF
#  $!ENDIF
#  $!AlterData  [|LOOP|]

#    Equation = '{newvarname} = your-equation'

#$!EndLoop

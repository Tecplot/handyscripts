# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from JobInfo import *
import subprocess
from textwrap import dedent

import time

instructionFile = sys.argv[1]
assert os.path.exists(instructionFile), '"%s" is not a valid instruction file.' % `instructionFile`

# Initialize the JobInfo object, which helps to process this job
jobInfo = JobInfo()
jobInfo.fromXMLFile(instructionFile)

macropath = os.path.join(os.getcwd(), 'temp.mcr')
print(macropath)

f = open(macropath, 'w')
print('#!MC 1410\n', file=f)

first = True
for caseID, dataFileName in jobInfo.dataFiles().iteritems(): 
    if first: 
        readfile = '$!READDATASET  "{0}"'.format(*dataFileName)
        
        f.write(readfile)
        
        f.write("""\
  READDATAOPTION = NEW
  RESETSTYLE = YES
  VARLOADMODE = BYNAME
  ASSIGNSTRANDIDS = YES
  
$!PLOTTYPE = CARTESIAN3D
$!FIELDLAYERS SHOWMESH = YES

$!VARSET |ZonesLoaded| = |NUMZONES|
$!VARSET |FieldMapsLoaded| = |NUMFIELDMAPS|
$!VARSET |LastNumZones| = |ZonesLoaded|
$!VARSET |LastNumFieldMaps| = |FieldMapsLoaded|
$!VARSET |curFieldMap| = 1
$!VARSET |curZone| = 1

$!LOOP |FieldMapsLoaded|
  $!FIELDMAP [|curFieldMap|]  MESH{{COLOR = {0}}}
  $!VARSET |curFieldMap| += 1
$!ENDLOOP
""".format("Custom 30"))
        first = False
    else:
        readfile = '$!READDATASET  "{0}"'.format(*dataFileName)
        f.write(readfile)
        
        f.write("""\
  READDATAOPTION = APPEND
  RESETSTYLE = NO
  VARLOADMODE = BYNAME
  ASSIGNSTRANDIDS = YES

$!VARSET |ZonesLoaded| = (|NUMZONES|-|LastNumZones|)
$!VARSET |FieldMapsLoaded| = (|NUMFIELDMAPS|-|LastNumFieldMaps|)
$!VARSET |LastNumZones| = (|ZonesLoaded|+|LastNumZones|)
$!VARSET |LastNumFieldMaps| = (|FieldMapsLoaded|+|LastNumFieldMaps|)


$!LOOP |FieldMapsLoaded|
  $!FIELDMAP [|curFieldMap|]  MESH{{COLOR = {0}}}
  $!VARSET |curFieldMap| += 1
$!ENDLOOP
""".format("Custom 30"))
    
exeme = 'C:/Program Files/Tecplot/Tecplot 360 EX Beta/bin/tec360.exe ' + macropath
print(exeme)
subprocess.call(exeme)


# Remove the instruction file now. This also tells Chorus that the job is no longer in progress.
#os.remove(instructionFile)


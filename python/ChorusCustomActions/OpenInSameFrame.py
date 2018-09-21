# -*- coding: utf-8 -*-

import sys
import os
from JobInfo import *
import subprocess

instructionFile = sys.argv[1]
assert os.path.exists(instructionFile), '"%s" is not a valid instruction file.' % `instructionFile`

# Initialize the JobInfo object, which helps to process this job
jobInfo = JobInfo()
jobInfo.fromXMLFile(instructionFile)

dataFiles = ""

for caseID, dataFile in jobInfo.dataFiles().iteritems(): 
    print dataFile
    dataFiles += dataFile[0] + " " 
    
exeme = 'C:/Program Files/Tecplot/Tecplot 360 EX Beta/bin/tec360.exe ' + dataFiles
print exeme
subprocess.call(exeme)

# Remove the instruction file now. This also tells Chorus that the job is no longer in progress.
os.remove(instructionFile)


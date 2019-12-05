import tecplot as tp
from tecplot.constant import PlotType
import numpy as np
import os

tp.session.connect()

f=tp.active_frame()
p=tp.active_page()
ds=f.dataset

#define the surface zone, the node index and the distance to be extracted
zoneNr=2-1#Tecplot indexes are 1-based
Zne=ds.zone(zoneNr)
nodeNr=754-1
distance=1

#Calculation of the normal vector
tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
    command=("Calculate Function='GRIDKUNITNORMAL' Normalization='None'"\
        +" ValueLocation='Nodal' CalculateOnDemand='F'"\
        +" UseMorePointsForFEGradientCalculations='F'"))

#Identification of var names for cordinates and normal vector
coordVars=['x','y','z']
vectorVars=['X Grid K Unit Normal','Y Grid K Unit Normal','Z Grid K Unit Normal']

#retrieves the start point(on the surface) and the end point of the line(offset)
surfPt=[Zne.values(i)[nodeNr] for i in coordVars]
endPt=[i+Zne.values(j)[nodeNr]*distance for i,j in zip(surfPt,vectorVars)]

#defines all of the points coordinates along the line:
linePts=np.zeros((3,100))
for i,(j,k) in enumerate(zip(surfPt,endPt)):
    linePts[i]=np.linspace(j, k, 100)

#extract the line in Tecplot
line = tp.data.extract.extract_line(zip(linePts[0],linePts[1],linePts[2]))

#Compute the distance along the line
tp.data.operate.execute_equation(equation=\
    '{Dist}=SQRT(({'+'X}'+'-{}'.format(surfPt[0])+')**2'\
        +'+({'+'Y}'+'-{}'.format(surfPt[1])+')**2'\
            +'+({'+'Z}'+'-{}'.format(surfPt[2])+')**2)',
    zones=line)

#Create a new frame for the plot
f2=p.add_frame()
f2.position=(4.3,5.0)
f2.height=3.2
f2.width=5.6
f2.plot_type=PlotType.XYLine
p=f2.plot()
p.delete_linemaps()
p.add_linemap()
p.linemap(0).name='Extracted Profile'
p.linemap(0).x_variable_index=3#default is the 4th variable
p.linemap(0).y_variable_index=ds.variable('Dist').index
p.linemap(0).zone_index=2
p.view.fit()
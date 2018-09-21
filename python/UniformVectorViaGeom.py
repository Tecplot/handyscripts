import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

# Uncomment the following line to connect to a running instance of Tecplot 360:
tp.session.connect()

tp.macro.execute_command("""$!ReadDataSet  '\"C:\\Program Files\\Tecplot\\Tecplot 360 EX Beta\\examples\\SimpleData\\VortexShedding.plt\" '
  ReadDataOption = New
  ResetStyle = Yes
  VarLoadMode = ByName
  AssignStrandIDs = Yes
  VarNameList = '\"X(M)\" \"Y(M)\" \"U(M/S)\" \"V(M/S)\" \"W(M/S)\" \"P(N/M2)\" \"T(K)\" \"R(KG/M3)\"'""")
tp.macro.execute_command('''$!Pick SetMouseMode
  MouseMode = Select''')
cmd = '''$!AttachGeom 
  PositionCoordsys = FRAME
  RawData
  1
  
'''
idxs= ""
count = 0
for i in range(10,100,1):
    for j in range(10,100,1):
        idxs += str(i) + ' ' + str(j) +'\n'
        count +=1
#print (count)
cmd+= str(count)+'\n' + idxs
print(cmd)
tp.macro.execute_command(cmd)

tp.macro.execute_command('''$!Pick AddAll
  SELECTGEOMS=YES''')
tp.macro.execute_command('''$!ExtractFromGeom 
  ExtractLinePointsOnly = Yes
  IncludeDistanceVar = No
  NumPts = 200
  ExtractToFile = No''')
#tp.macro.execute_command('''$!Pick Clear''')
  
tp.active_frame().plot().fieldmap(0).vector.show=False
tp.active_frame().plot(PlotType.Cartesian2D).vector.u_variable_index=2
tp.active_frame().plot(PlotType.Cartesian2D).vector.v_variable_index=3
tp.active_frame().plot().show_vector=True
tp.active_frame().plot().fieldmap(1).vector.tangent_only=True
tp.active_frame().plot().fieldmap(1).vector.tangent_only=False


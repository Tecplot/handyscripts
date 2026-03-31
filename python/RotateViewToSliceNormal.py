import math
import tecplot as tp

#Toggle on Scripting>PyTecplot Connections>Accept connections in Tecplot 360 GUI
#Place an arbitrary slice 
#Run this script to change the 3D orientation view to face the normal direction of that slice

tp.session.connect()
plot = tp.active_frame().plot()
slice = plot.slice(0)
x_norm, y_norm, z_norm = slice.arbitrary_normal

plot.view.psi = math.degrees(math.acos(z_norm))
plot.view.theta = -90-math.degrees(math.atan2(y_norm,x_norm))
plot.view.alpha = 0
plot.view.fit()
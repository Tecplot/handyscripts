formula_restart_version: 1
Dxx
VecX(grad("u-velocity"))
Dyy
VecY(grad("v-velocity"))
Dzz
VecZ(grad("w-velocity"))
Dxy
VecY(grad("u-velocity"))
Dyx
VecX(grad("v-velocity"))
Dxz
VecZ(grad("u-velocity"))
Dzx
VecX(grad("w-velocity"))
Dyz
VecZ(grad("v-velocity"))
Dzy
VecY(grad("w-velocity"))
DELxx
"Dxx"^2
DELyy
"Dyy"^2
DELzz
"Dzz"^2
DELxy
("Dxy"+"Dyx")^2
DELxz
("Dxz"+"Dzx")^2
DELyz
("Dyz"+"Dzy")^2
D:D
4*("DELxx"+"DELyy"+"DELzz")+2*("DELxy"+"DELxz"+"DELyz")
mag(vorticity)
mag(curl("velocity"))
shear
sqrt(0.5*"D:D")
lambda
("shear"+0.5E-06)/("shear"+"mag(vorticity)"+1.0E-06)
nrmlz('velocity')
nrmlz("velocity")
mag('velocity')
mag("velocity")
'velocity' dot (curl('velocity'))
"velocity" dot (curl("velocity"))
nnviscosity
41.7/("shear"+1.0E-06)+0.0115*exp(-4.52E-05*"shear")
Conc Variance
("species conc 1"-0.5)^2

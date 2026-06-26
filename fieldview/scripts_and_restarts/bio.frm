formula_restart_version: 1
Velmag
mag("velocity")
nrmlz('velocity')
nrmlz("velocity")
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
mag('velocity')
mag("velocity")
'velocity' dot (curl('velocity'))
"velocity" dot (curl("velocity"))
stress
0.01*"shear"
Nconvective
"species conc 1"*"w-velocity"
Ndiff
-.05*grad("species conc 1")
Normal
nrmlz(-grad(mag("velocity")))
Ndiff-Normal
"Ndiff" dot "Normal"

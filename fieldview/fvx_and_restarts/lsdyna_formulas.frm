formula_restart_version: 1
StrainRate-xx
VecX(grad("Velocity-x"))
StrainRate-yy
VecY(grad("Velocity-y"))
StrainRate-zz
VecZ(grad("Velocity-z"))
StrainRate-xy
(VecX(grad("Velocity-y"))+VecY(grad("Velocity-x")))/2
StrainRate-yz
(VecY(grad("Velocity-z"))+VecZ(grad("Velocity-y")))/2
StrainRate-zx
(VecZ(grad("Velocity-x"))+VecX(grad("Velocity-z")))/2
pressure [LS-DYNA]
(-1*("Stress-xx")+-1*("Stress-yy")+-1*("Stress-zz"))/3
result-velocity [LS-DYNA]
mag("Velocity")
Strain-Mean [LS-DYNA]
("Strain-xx"+"Strain-yy"+"Strain-zz")/3
Strain-Effective [LS-DYNA]
sqrt(( ("Strain-xx"-"Strain-yy")^2+("Strain-yy"-"Strain-zz")^2+("Strain-zz"-"Strain-xx")^2 )/2+3*("Strain-xy"^2+"Strain-yz"^2+"Strain-zx"^2))
Strain-Invariant-1 [LS-DYNA]
"Strain-xx"+"Strain-yy"+"Strain-zz"
Strain-Invariant-2 [LS-DYNA]
"Strain-xx"*"Strain-yy"+"Strain-yy"*"Strain-zz"+"Strain-xx"*"Strain-zz"-"Strain-xy"^2-"Strain-yz"^2-"Strain-zx"^2
Strain-Invariant-3 [LS-DYNA]
"Strain-xx"*"Strain-yy"*"Strain-zz"+2*"Strain-xy"*"Strain-yz"*"Strain-zx"-"Strain-xx"*"Strain-yz"^2-"Strain-yy"*"Strain-zx"^2-"Strain-zz"*"Strain-xy"^2
Strain-Deviatoric-Invariant-2 [LS-DYNA]
("Strain-xx"-"Strain-Mean [LS-DYNA]")*("Strain-yy"-"Strain-Mean [LS-DYNA]")+("Strain-yy"-"Strain-Mean [LS-DYNA]")*("Strain-zz"-"Strain-Mean [LS-DYNA]")+("Strain-xx"-"Strain-Mean [LS-DYNA]")*("Strain-zz"-"Strain-Mean [LS-DYNA]")-"Strain-xy"^2-"Strain-yz"^2-"Strain-zx"^2
Strain-Deviatoric-Invariant-3 [LS-DYNA]
("Strain-xx"-"Strain-Mean [LS-DYNA]")*("Strain-yy"-"Strain-Mean [LS-DYNA]")*("Strain-zz"-"Strain-Mean [LS-DYNA]")+2*"Strain-xy"*"Strain-yz"*"Strain-zx"-("Strain-xx"-"Strain-Mean [LS-DYNA]")*"Strain-yz"^2-("Strain-yy"-"Strain-Mean [LS-DYNA]")*"Strain-zx"^2-("Strain-zz"-"Strain-Mean [LS-DYNA]")*"Strain-xy"^2
Strain-xy-Principal-Max [LS-DYNA]
("Strain-xx"+"Strain-yy")/2 + sqrt( (("Strain-xx"-"Strain-yy")/2)^2 + "Strain-xy"^2)
Strain-xy-Principal-Min [LS-DYNA]
("Strain-xx"+"Strain-yy")/2 - sqrt( (("Strain-xx"-"Strain-yy")/2)^2 + "Strain-xy"^2)
Strain-xz-Principal-Max [LS-DYNA]
("Strain-xx"+"Strain-zz")/2 + sqrt( (("Strain-xx"-"Strain-zz")/2)^2 + "Strain-zx"^2)
Strain-xz-Principal-Min [LS-DYNA]
("Strain-xx"+"Strain-zz")/2 - sqrt( (("Strain-xx"-"Strain-zz")/2)^2 + "Strain-zx"^2)
Strain-yz-Principal-Max [LS-DYNA]
("Strain-yy"+"Strain-zz")/2 + sqrt( (("Strain-yy"-"Strain-zz")/2)^2 + "Strain-yz"^2)
Strain-yz-Principal-Min [LS-DYNA]
("Strain-yy"+"Strain-zz")/2 - sqrt( (("Strain-yy"-"Strain-zz")/2)^2 + "Strain-yz"^2)
Strain-xy-Deviatoric-Principal-Max [LS-DYNA]
(("Strain-xx"-"Strain-Mean [LS-DYNA]")+("Strain-yy"-"Strain-Mean [LS-DYNA]"))/2 + sqrt( ((("Strain-xx"-"Strain-Mean [LS-DYNA]")-("Strain-yy"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-xy"^2)
Strain-xy-Deviatoric-Principal-Min [LS-DYNA]
(("Strain-xx"-"Strain-Mean [LS-DYNA]")+("Strain-yy"-"Strain-Mean [LS-DYNA]"))/2 - sqrt( ((("Strain-xx"-"Strain-Mean [LS-DYNA]")-("Strain-yy"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-xy"^2)
Strain-xz-Deviatoric-Principal-Max [LS-DYNA]
(("Strain-xx"-"Strain-Mean [LS-DYNA]")+("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2 + sqrt( ((("Strain-xx"-"Strain-Mean [LS-DYNA]")-("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-zx"^2)
Strain-xz-Deviatoric-Principal-Min [LS-DYNA]
(("Strain-xx"-"Strain-Mean [LS-DYNA]")+("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2 - sqrt( ((("Strain-xx"-"Strain-Mean [LS-DYNA]")-("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-zx"^2)
Strain-yz-Deviatoric-Principal-Max [LS-DYNA]
(("Strain-yy"-"Strain-Mean [LS-DYNA]")+("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2 + sqrt( ((("Strain-yy"-"Strain-Mean [LS-DYNA]")-("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-yz"^2)
Strain-yz-Deviatoric-Principal-Min [LS-DYNA]
(("Strain-yy"-"Strain-Mean [LS-DYNA]")+("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2 - sqrt( ((("Strain-yy"-"Strain-Mean [LS-DYNA]")-("Strain-zz"-"Strain-Mean [LS-DYNA]"))/2)^2 + "Strain-yz"^2)
Stress-Mean [LS-DYNA]
("Stress-xx"+"Stress-yy"+"Stress-zz")/3
Stress-Effective [LS-DYNA]
sqrt(( ("Stress-xx"-"Stress-yy")^2+("Stress-yy"-"Stress-zz")^2+("Stress-zz"-"Stress-xx")^2 )/2+3*("Stress-xy"^2+"Stress-yz"^2+"Stress-zx"^2))
Stress-Invariant-1 [LS-DYNA]
("Stress-xx"+"Stress-yy"+"Stress-zz")
Stress-Invariant-2 [LS-DYNA]
"Stress-xx"*"Stress-yy"+"Stress-yy"*"Stress-zz"+"Stress-xx"*"Stress-zz"-"Stress-xy"^2-"Stress-yz"^2-"Stress-zx"^2
Stress-Invariant-3 [LS-DYNA]
"Stress-xx"*"Stress-yy"*"Stress-zz"+2*"Stress-xy"*"Stress-yz"*"Stress-zx"-"Stress-xx"*"Stress-yz"^2-"Stress-yy"*"Stress-zx"^2-"Stress-zz"*"Stress-xy"^2
Stress-Deviatoric-Invariant2 [LS-DYNA]
("Stress-xx"-"Stress-Mean [LS-DYNA]")*("Stress-yy"-"Stress-Mean [LS-DYNA]")+("Stress-yy"-"Stress-Mean [LS-DYNA]")*("Stress-zz"-"Stress-Mean [LS-DYNA]")+("Stress-xx"-"Stress-Mean [LS-DYNA]")*("Stress-zz"-"Stress-Mean [LS-DYNA]")-"Stress-xy"^2-"Stress-yz"^2-"Stress-zx"^2
Stress-Deviatoric-Invariant-3 [LS-DYNA]
("Stress-xx"-"Stress-Mean [LS-DYNA]")*("Stress-yy"-"Stress-Mean [LS-DYNA]")*("Stress-zz"-"Stress-Mean [LS-DYNA]")+2*"Stress-xy"*"Stress-yz"*"Stress-zx"-("Stress-xx"-"Stress-Mean [LS-DYNA]")*"Stress-yz"^2-("Stress-yy"-"Stress-Mean [LS-DYNA]")*"Stress-zx"^2-("Stress-zz"-"Stress-Mean [LS-DYNA]")*"Stress-xy"^2
Stress-xy-Principal-Max [LS-DYNA]
("Stress-xx"+"Stress-yy")/2 + sqrt( (("Stress-xx"-"Stress-yy")/2)^2 + "Stress-xy"^2)
Stress-xy-Principal-Min [LS-DYNA]
("Stress-xx"+"Stress-yy")/2 - sqrt( (("Stress-xx"-"Stress-yy")/2)^2 + "Stress-xy"^2)
Stress-xz-Principal-Max [LS-DYNA]
("Stress-xx"+"Stress-zz")/2 + sqrt( (("Stress-xx"-"Stress-zz")/2)^2 + "Stress-zx"^2)
Stress-xz-Principal-Min [LS-DYNA]
("Stress-xx"+"Stress-zz")/2 - sqrt( (("Stress-xx"-"Stress-zz")/2)^2 + "Stress-zx"^2)
Stress-yz-Principal-Max [LS-DYNA]
("Stress-yy"+"Stress-zz")/2 + sqrt( (("Stress-yy"-"Stress-zz")/2)^2 + "Stress-yz"^2)
Stress-yz-Principal-Min [LS-DYNA]
("Stress-yy"+"Stress-zz")/2 - sqrt( (("Stress-yy"-"Stress-zz")/2)^2 + "Stress-yz"^2)
Stress-xy-Deviatoric-Principal-Max [LS-DYNA]
(("Stress-xx"-"Stress-Mean [LS-DYNA]")+("Stress-yy"-"Stress-Mean [LS-DYNA]"))/2 + sqrt( ((("Stress-xx"-"Stress-Mean [LS-DYNA]")-("Stress-yy"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-xy"^2)
Stress-xy-Deviatoric-Principal-Min [LS-DYNA]
(("Stress-xx"-"Stress-Mean [LS-DYNA]")+("Stress-yy"-"Stress-Mean [LS-DYNA]"))/2 - sqrt( ((("Stress-xx"-"Stress-Mean [LS-DYNA]")-("Stress-yy"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-xy"^2)
Stress-xz-Deviatoric-Principal-Max [LS-DYNA]
(("Stress-xx"-"Stress-Mean [LS-DYNA]")+("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2 + sqrt( ((("Stress-xx"-"Stress-Mean [LS-DYNA]")-("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-zx"^2)
Stress-xz-Deviatoric-Principal-Min [LS-DYNA]
(("Stress-xx"-"Stress-Mean [LS-DYNA]")+("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2 - sqrt( ((("Stress-xx"-"Stress-Mean [LS-DYNA]")-("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-zx"^2)
Stress-yz-Deviatoric-Principal-Max [LS-DYNA]
(("Stress-yy"-"Stress-Mean [LS-DYNA]")+("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2 + sqrt( ((("Stress-yy"-"Stress-Mean [LS-DYNA]")-("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-yz"^2)
Stress-yz-Deviatoric-Principal-Min [LS-DYNA]
(("Stress-yy"-"Stress-Mean [LS-DYNA]")+("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2 - sqrt( ((("Stress-yy"-"Stress-Mean [LS-DYNA]")-("Stress-zz"-"Stress-Mean [LS-DYNA]"))/2)^2 + "Stress-yz"^2)
StrainRate-Mean [LS-DYNA]
("StrainRate-xx"+"StrainRate-yy"+"StrainRate-zz")/3
StrainRate-Effective [LS-DYNA]
sqrt(( ("StrainRate-xx"-"StrainRate-yy")^2+("StrainRate-yy"-"StrainRate-zz")^2+("StrainRate-zz"-"StrainRate-xx")^2 )/2+3*("StrainRate-xy"^2+"StrainRate-yz"^2+"StrainRate-zx"^2))
StrainRate-Invariant-1 [LS-DYNA]
("StrainRate-xx"+"StrainRate-yy"+"StrainRate-zz")
StrainRate-Invariant-2 [LS-DYNA]
"StrainRate-xx"*"StrainRate-yy"+"StrainRate-yy"*"StrainRate-zz"+"StrainRate-xx"*"StrainRate-zz"-"StrainRate-xy"^2-"StrainRate-yz"^2-"StrainRate-zx"^2
StrainRate-Invariant-3 [LS-DYNA]
"StrainRate-xx"*"StrainRate-yy"*"StrainRate-zz"+2*"StrainRate-xy"*"StrainRate-yz"*"StrainRate-zx"-"StrainRate-xx"*"StrainRate-yz"^2-"StrainRate-yy"*"StrainRate-zx"^2-"StrainRate-zz"*"StrainRate-xy"^2
StrainRate-Deviatoric-Invariant-2 [LS-DYNA]
("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")*("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")*("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")*("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]")-"StrainRate-xy"^2-"StrainRate-yz"^2-"StrainRate-zx"^2
StrainRate-Deviatoric-Invariant-3 [LS-DYNA]
("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")*("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")*("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]")+2*"StrainRate-xy"*"StrainRate-yz"*"StrainRate-zx"-("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")*"StrainRate-yz"^2-("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")*"StrainRate-zx"^2-("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]")*"StrainRate-xy"^2
StrainRate-xy-Principal-Max [LS-DYNA]
("StrainRate-xx"+"StrainRate-yy")/2 + sqrt( (("StrainRate-xx"-"StrainRate-yy")/2)^2 + "StrainRate-xy"^2)
StrainRate-xy-Principal-Min [LS-DYNA]
("StrainRate-xx"+"StrainRate-yy")/2 - sqrt( (("StrainRate-xx"-"StrainRate-yy")/2)^2 + "StrainRate-xy"^2)
StrainRate-xz-Principal-Max [LS-DYNA]
("StrainRate-xx"+"StrainRate-zz")/2 + sqrt( (("StrainRate-xx"-"StrainRate-zz")/2)^2 + "StrainRate-zx"^2)
StrainRate-xz-Principal-Min [LS-DYNA]
("StrainRate-xx"+"StrainRate-zz")/2 - sqrt( (("StrainRate-xx"-"StrainRate-zz")/2)^2 + "StrainRate-zx"^2)
StrainRate-yz-Principal-Max [LS-DYNA]
("StrainRate-yy"+"StrainRate-zz")/2 + sqrt( (("StrainRate-yy"-"StrainRate-zz")/2)^2 + "StrainRate-yz"^2)
StrainRate-yz-Principal-Min [LS-DYNA]
("StrainRate-yy"+"StrainRate-zz")/2 - sqrt( (("StrainRate-yy"-"StrainRate-zz")/2)^2 + "StrainRate-yz"^2)
StrainRate-xy-Deviatoric-Principal-Max [LS-DYNA]
(("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]"))/2 + sqrt( ((("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-xy"^2)
StrainRate-xy-Deviatoric-Principal-Min [LS-DYNA]
(("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]"))/2 - sqrt( ((("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-xy"^2)
StrainRate-xz-Deviatoric-Principal-Max [LS-DYNA]
(("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2 + sqrt( ((("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-zx"^2)
StrainRate-xz-Deviatoric-Principal-Min [LS-DYNA]
(("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2 - sqrt( ((("StrainRate-xx"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-zx"^2)
StrainRate-yz-Deviatoric-Principal-Max [LS-DYNA]
(("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2 + sqrt( ((("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-yz"^2)
StrainRate-yz-Deviatoric-Principal-Min [LS-DYNA]
(("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")+("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2 - sqrt( ((("StrainRate-yy"-"StrainRate-Mean [LS-DYNA]")-("StrainRate-zz"-"StrainRate-Mean [LS-DYNA]"))/2)^2 + "StrainRate-yz"^2)

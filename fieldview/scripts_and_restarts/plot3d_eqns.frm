formula_restart_version: 1
Momentum Vectors [PLOT3D]
"x-momentum (Q2)"*unitx+"y-momentum (Q3)"*unity+"z-momentum (Q4)"*unitz
Normalized density [PLOT3D]
"Density (Q1)"
Stagnation density [PLOT3D]
"Density (Q1)"*(1.+(0.2*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))))^2.5
Norm. stag. density [PLOT3D]
"Stagnation density [PLOT3D]"/((1.0+0.2*FSMach^2)^2.5)
Log(norm. density) [PLOT3D]
ln("Normalized density [PLOT3D]")
Pressure [PLOT3D]
0.4*("Stag. energy (Q5)"-0.5*"Density (Q1)"*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))
Norm. pressure [PLOT3D]
1.4*"Pressure [PLOT3D]"
Stagnation press. [PLOT3D]
"Pressure [PLOT3D]"*(1.0+0.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))^3.5
Norm. stag. press. [PLOT3D]
"Stagnation press. [PLOT3D]"*1.4/((1.0+0.2*FSMach^2)^3.5)
Cp [PLOT3D]
("Pressure [PLOT3D]"-1.0/1.4)/(0.5*FSMach^2)
Stagnation Cp [PLOT3D]
("Stagnation press. [PLOT3D]"-((1.0+0.2*FSMach^2)^3.5)/1.4)/(0.5*FSMach^2)
Pitot pressure [PLOT3D]
((1.-(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))/(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))+1.E-12)))*((1.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))))^3.5/(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))*2.8/2.4-0.4/2.4)^2.5)+(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))/(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))+1.E-12))*((1.+0.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))))^3.5))*"Pressure [PLOT3D]"
Pitot pressure ratio [PLOT3D]
((1.-(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))/(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))+1.E-12)))*((1.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))))^3.5/(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))*2.8/2.4-0.4/2.4)^2.5)+(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))/(((((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.)-abs(((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))-1.))+1.E-12))*((1.+0.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))))^3.5))*(0.56*("Stag. energy (Q5)"-0.5*"Density (Q1)"*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)))
Dynamic pressure [PLOT3D]
0.5*("x-momentum (Q2)"^2+"y-momentum (Q3)"^2+"z-momentum (Q4)"^2)/"Density (Q1)"
Log(norm. pressure) [PLOT3D]
ln("Norm. pressure [PLOT3D]")
Temperature [PLOT3D]
"Pressure [PLOT3D]"/"Density (Q1)"
Norm. temperature [PLOT3D]
1.4*"Temperature [PLOT3D]"
Stag. temperature [PLOT3D]
"Temperature [PLOT3D]"*(1.0+0.2*((("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))/(0.56*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))))
Norm. stag. temp. [PLOT3D]
"Stag. temperature [PLOT3D]"*1.4/(1.0+0.2*FSMach^2)
Log(norm. temp.) [PLOT3D]
ln("Norm. temperature [PLOT3D]")
Enthalpy [PLOT3D]
1.4*("Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2))
Norm. enthalpy [PLOT3D]
0.4*"Enthalpy [PLOT3D]"
Stag. enthalpy [PLOT3D]
"Enthalpy [PLOT3D]"+0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)
Norm.stag.enthalpy [PLOT3D]
"Stag. enthalpy [PLOT3D]"/(2.5+0.5*FSMach^2)
(Internal) energy [PLOT3D]
"Stag. energy (Q5)"/"Density (Q1)"-0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)
Norm. int. energy [PLOT3D]
0.56*"(Internal) energy [PLOT3D]"
Stagnation energy [PLOT3D]
"Stag. energy (Q5)"/"Density (Q1)"
Norm. stag. energy [PLOT3D]
"Stagnation energy [PLOT3D]"/(1.0/0.56+0.5*FSMach^2)
Kinetic energy [PLOT3D]
0.5*(("x-momentum (Q2)"/"Density (Q1)")^2+("y-momentum (Q3)"/"Density (Q1)")^2+("z-momentum (Q4)"/"Density (Q1)")^2)
Norm. kin. energy [PLOT3D]
"Kinetic energy [PLOT3D]"*2.0/FSMach^2
u-velocity [PLOT3D]
"x-momentum (Q2)"/"Density (Q1)"
v-velocity [PLOT3D]
"y-momentum (Q3)"/"Density (Q1)"
w-velocity [PLOT3D]
"z-momentum (Q4)"/"Density (Q1)"
Velocity Magnitude [PLOT3D]
sqrt("u-velocity [PLOT3D]"^2+"v-velocity [PLOT3D]"^2+"w-velocity [PLOT3D]"^2)
Mach number [PLOT3D]
sqrt(("u-velocity [PLOT3D]"^2+"v-velocity [PLOT3D]"^2+"w-velocity [PLOT3D]"^2)/(0.4*"Enthalpy [PLOT3D]"))
Speed of sound [PLOT3D]
sqrt(0.4*"Enthalpy [PLOT3D]")
Cross flow velocity [PLOT3D]
sqrt("y-momentum (Q3)"^2+"z-momentum (Q4)"^2)/"Density (Q1)"
Div. of velocity [PLOT3D]
-(("Momentum Vectors [PLOT3D]"/"Density (Q1)") dot (grad("Density (Q1)")/"Density (Q1)"))
Entropy [PLOT3D]
2.5*ln(1.4*"Pressure [PLOT3D]"/("Density (Q1)"^1.4))
Entropy measure s1 [PLOT3D]
1.4*"Pressure [PLOT3D]"/("Density (Q1)"^1.4)-1.0
vorticity (x-dir) [PLOT3D]
VecX(curl("Momentum Vectors [PLOT3D]"/"Density (Q1)"))
vorticity (y-dir) [PLOT3D]
VecY(curl("Momentum Vectors [PLOT3D]"/"Density (Q1)"))
vorticity (z-dir) [PLOT3D]
VecZ(curl("Momentum Vectors [PLOT3D]"/"Density (Q1)"))
Vorticity Magnitude [PLOT3D]
mag(curl("Momentum Vectors [PLOT3D]"/"Density (Q1)"))
Swirl [PLOT3D]
((curl("Momentum Vectors [PLOT3D]"/"Density (Q1)")) dot "Momentum Vectors [PLOT3D]")/("x-momentum (Q2)"^2+"y-momentum (Q3)"^2+"z-momentum (Q4)"^2)
Vel. x Vort. mag. [PLOT3D]
mag(("Momentum Vectors [PLOT3D]"/"Density (Q1)") cross (curl(("Momentum Vectors [PLOT3D]")/"Density (Q1)")))
Helicity density [PLOT3D]
(curl("Momentum Vectors [PLOT3D]"/"Density (Q1)")) dot ("Momentum Vectors [PLOT3D]")/"Density (Q1)"
Relative helicity [PLOT3D]
((curl("Momentum Vectors [PLOT3D]"/"Density (Q1)")) dot "Momentum Vectors [PLOT3D]")/(sqrt("x-momentum (Q2)"^2+"y-momentum (Q3)"^2+"z-momentum (Q4)"^2)*"Vorticity Magnitude [PLOT3D]")
Filter.rel.helicity [PLOT3D]
((abs("Helicity density [PLOT3D]")-(0.1*FSMach^2))+abs((abs("Helicity density [PLOT3D]")-(0.1*FSMach^2))))/(2.0*(abs("Helicity density [PLOT3D]")-(0.1*FSMach^2)))*"Relative helicity [PLOT3D]"
Shock function [PLOT3D]
(("Momentum Vectors [PLOT3D]"/"Density (Q1)") dot (grad("Pressure [PLOT3D]")))/(mag(grad("Pressure [PLOT3D]"))*"Speed of sound [PLOT3D]")
Filter. shock func. [PLOT3D]
(((mag(grad("Pressure [PLOT3D]"))^2)-0.01)+abs(((mag(grad("Pressure [PLOT3D]"))^2)-0.01)))/(2.0*((mag(grad("Pressure [PLOT3D]"))^2)-0.01))*"Shock function [PLOT3D]"
Press.gradient mag. [PLOT3D]
mag(grad("Pressure [PLOT3D]"))
Dens. gradient mag. [PLOT3D]
mag(grad("Density (Q1)"))
Velocity Vectors [PLOT3D]
"Momentum Vectors [PLOT3D]"/"Density (Q1)"
Vorticity Vectors [PLOT3D]
curl("Velocity Vectors [PLOT3D]")
Pert. vel. Vectors [PLOT3D]
("Momentum Vectors [PLOT3D]"/"Density (Q1)") - (FSMach*cos(Alpha)*grad("X")+FSMach*sin(Alpha)*grad("Y"))
Vel.xVort. Vectors [PLOT3D]
("Momentum Vectors [PLOT3D]"/"Density (Q1)") cross (curl(("Momentum Vectors [PLOT3D]")/"Density (Q1)"))
Press.grad Vectors [PLOT3D]
grad("Pressure [PLOT3D]")
Dens. grad Vectors [PLOT3D]
grad("Density (Q1)")

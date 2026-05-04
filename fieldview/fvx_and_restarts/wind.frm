formula_restart_version:1
u-vel [WIND]
"rho*u, x-momentum"/"rho, density"
v-vel [WIND]
"rho*v, y-momentum"/"rho, density"
w-vel [WIND]
"rho*w, z-momentum"/"rho, density"
e0 [WIND]
"rho*e0, stagnation energy"/"rho, density"
V**2/2 [WIND]
.5*("rho*u, x-momentum"^2+"rho*v, y-momentum"^2+"rho*w, z-momentum"^2)/("rho, density"^2)
Velocity [WIND]
UnitX*"u-vel [WIND]"+UnitY*"v-vel [WIND]"+UnitZ*"w-vel [WIND]"
Velocity [shock]
UnitX*"u-vel [WIND]"+UnitY*"v-vel [WIND]"+UnitZ*"w-vel [WIND]"
Velocity Magnitude [WIND]
((("rho*u, x-momentum"^2+"rho*v, y-momentum"^2+"rho*w, z-momentum"^2)/("rho, density"^2))^0.5)
Pressure [WIND]
( Gamma-1)*("rho, density")*("e0 [WIND]"-"V**2/2 [WIND]")
Pressure(lbf/in2) [WIND]
( Gamma-1)*("rho, density")*("e0 [WIND]"-"V**2/2 [WIND]")/144.
Pressure [shock]
( Gamma-1)*("rho, density")*("e0 [WIND]"-"V**2/2 [WIND]")
density [shock]
"rho, density"
Temperature [WIND]
( Gamma-1)*("rho, density")*("e0 [WIND]"-"V**2/2 [WIND]")/("rho, density"*R)
Cp [WIND]
(2/( Gamma*FSMach*FSMach))*("Pressure [WIND]"/Pinf-1)
Speed of Sound [WIND]
((Gamma*R*"Temperature [WIND]")^0.5)
Mach Number [WIND]
("Velocity Magnitude [WIND]")/("Speed of Sound [WIND]")
Mach [shock]
("Velocity Magnitude [WIND]")/("Speed of Sound [WIND]")
Stagnation Pressure [WIND]
("Pressure [WIND]")*((1+(((Gamma-1)/2)*(("Mach Number [WIND]")^2)))^(Gamma/(Gamma-1)))
Stagnation Temperature [WIND]
("Temperature [WIND]")*(1+((Gamma-1)/2)*("Mach Number [WIND]")^2)
Enthalpy [WIND]
( Gamma)*("e0 [WIND]"-"V**2/2 [WIND]")
total enthalpy [shock]
"Enthalpy [WIND]"+"V**2/2 [WIND]"
Entropy [WIND]
( R/( Gamma-1))*ln(("Pressure [WIND]"/Pinf)/(("rho, density"/(Pinf/(R*Tinf)))^ Gamma))
Pt/Pt0 [WIND]
"Stagnation Pressure [WIND]" / ( Pinf*(1+(Gamma-1)/2*FSMach*FSMach)^(Gamma/(Gamma-1)) )
T0/T0inf [WIND]
"Stagnation Temperature [WIND]" / ( Tinf*(1+(Gamma-1)/2*FSMach*FSMach) )
Local Alpha [deg]
(180/PI)*atan("rho*v, y-momentum"/"rho*u, x-momentum")
Local Beta [deg]
(180/PI)*asin("rho*w, z-momentum"/"Velocity Magnitude [WIND]"/"rho, density")
mu [Sutherland]
3.8158e-7 * ("Temperature [WIND]"/524.07)^1.5 * (524.07+216.0)/("Temperature [WIND]" + 216.0)
Q-rad, radiative heat flux [BTU/s-ft^2]
4.7565e-13*"Temperature [WIND]"^4
Cell Reynolds Number
"rho, density"*"Speed of Sound [WIND]"*2.*"Wall Cell Height"/"mu [Sutherland]"
Skin Friction Vector
"Cfx [WIND]" * UnitX + "Cfy [WIND]" * UnitY + "Cfz [WIND]" * UnitZ
Skin Friction Coefficient
mag("Skin Friction Vector")
y plus
"Wall Cell Height"*FSMach*sqrt("Skin Friction Coefficient"*Gamma/2.*Pinf*"rho, density")/"mu [Sutherland]"
Pseudo-Schlieren (y)
Abs(VecY(Grad("rho, density"/Pinf*R*Tinf)))
Pressure [Real Gas]
"p, pressure"
Pressure2 [Real Gas]
("Beta"-1)*("rho*e0, stagnation energy"-0.5*("rho*u, x-momentum"^2+"rho*v, y-momentum"^2+"rho*w, z-momentum"^2)/"rho, density")
Pressure (lbf/in2) [Real Gas]
"Pressure [Real Gas]"/144.
Temperature [Real Gas]
"Pressure [Real Gas]"/("rho, density"*R*"Z, compressibilty")
Cp [Real Gas]
(2/( Gamma*FSMach*FSMach))*("Pressure [Real Gas]"/Pinf-1)
Speed of Sound [Real Gas]
"a, local speed of sound"
Speed of Sound2 [Real Gas]
(Gamma*R*"Z, compressibilty"*"Temperature [Real Gas]")^0.5
Mach Number [Real Gas]
("Velocity Magnitude [WIND]")/("Speed of Sound [Real Gas]")
Vorticity
curl("momentum"/"rho, density")
Isentropic Mach Number
(2/(Gamma-1)*((1+(Gamma-1)/2*FSMach*FSMach)*("Pressure [WIND]"/Pinf)^((1-Gamma)/Gamma)-1))^0.5
Shear1
VecX(grad("u-vel [WIND]"))*UnitX+VecY(grad("v-vel [WIND]"))*UnitY+VecZ(grad("w-vel [WIND]"))*UnitZ
Shear2
grad("u-vel [WIND]")-VecX(grad("u-vel [WIND]"))*UnitX+VecX(grad("v-vel [WIND]"))*UnitY+VecZ(grad("v-vel [WIND]"))*UnitX+VecY(grad("w-vel [WIND]"))*UnitX+VecX(grad("w-vel [WIND]"))*UnitZ
Q criterion (vortex positive)
("Vorticity" dot "Vorticity"-2*"Shear1" dot "Shear1"-"Shear2" dot "Shear2")/4
Q criterion (modified, vortex positive)
(sqrt("Vorticity" dot "Vorticity"/8)-sqrt("Shear1" dot "Shear1"/2+"Shear2" dot "Shear2"/8))/2
Hussein lambda2 (vortex negative)
sqrt(grad("u-vel [WIND]") dot grad("u-vel [WIND]")+grad("v-vel [WIND]") dot grad("v-vel [WIND]")+grad("w-vel [WIND]") dot grad("w-vel [WIND]"))-mag("Vorticity")

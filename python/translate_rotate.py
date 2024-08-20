"""
Script has two parts, first to translate to XYZ location. This point will be the new origin. All rotations or transformations will be about that new origin.
params:
-zone_num where data is located.
-index I of the XYZ location of interest.

Second part rotates about the new origin. In this case the rotation is about a 2D plane, which only requires one angle, theta. 

A general 3D rotation formulation is given beneath. This should be able to rotate (and translate) any point in cartesian grid.
"""


import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import math
import numpy as np

# doesn't need to be in connected mode, but it's easier to see what's happening.
tp.session.connect()

# this creates a variable corresponding to the index value of every cell/node.
tp.data.operate.execute_equation(equation="{I} = I")

# supply the zone and index you want to move to. 
# Note: You can pick nearest node and therefore exact I, by using ctrl + click with the probe tool in Tecplot
zone_num = 0
I = 778

ds = tp.active_frame().dataset
zone = ds.zone(zone_num)
new_x = ds.variable("x").values(zone)[I-1] # subtract 1 because Tecplot is 1-indexed, python is 0-indexed. 
new_y = ds.variable("y").values(zone)[I-1]
new_z = ds.variable("z").values(zone)[I-1]

# translate to new XYZ
tp.data.operate.execute_equation(equation=f"{{x}} = {{x}} - {new_x}")
tp.data.operate.execute_equation(equation=f"{{y}} = {{y}} - {new_y}")
tp.data.operate.execute_equation(equation=f"{{z}} = {{z}} - {new_z}")




# Now, globally rotate XZ plane about this point with desired theta, converted to radian.
theta = 90
theta_radian = np.radians(theta)
tp.data.operate.execute_equation(equation=f"{{x}} = {{x}} * cos({theta_radian}) + {{z}}*sin({theta_radian})")
tp.data.operate.execute_equation(equation=f"{{z}} = {{z}} * cos({theta_radian}) - {{x}}*sin({theta_radian})")



def arbitrary_xyz_rotation(alpha, beta, gamma, x=0, y=0, z=0):
    """
    Params:
    Provide 3 angles in degrees
    Assumes xyz = origin, but this can be changed.

    General rotation matrices taken from https://en.wikipedia.org/wiki/Rotation_matrix
    Rotations are applied sequentially. I'm sure it could be one equation, but that sounds more confusing.

    3D rotation requires three degrees of freedom
    yaw -> XY -> alpha
    pitch -> XZ -> βeta
    roll -> YZ -> gamma

                Z
                |
                |   
                |      
              β | γ 
               \|/   
                o----+------ Y
               / \    
              /   α
             /       
            X        
    """

    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)
    gamma_rad = np.radians(gamma)

    # Order matters! Matrix multiplication not commutative!

    # GAMMA/ROLL rotation
    tp.data.operate.execute_equation(f"{{y}} = {{y}} * cos({gamma_rad}) - {{z}} * sin({gamma_rad})")
    tp.data.operate.execute_equation(f"{{z}} = {{y}} * sin({gamma_rad}) + {{z}} * cos({gamma_rad})")

    # BETA/PITCH rotation
    tp.data.operate.execute_equation(f"{{x}} = {{x}} * cos({beta_rad}) + {{z}} * sin({beta_rad})")
    tp.data.operate.execute_equation(f"{{z}} = -{{x}} * sin({beta_rad}) + {{z}} * cos({beta_rad})")

    # ALPHA/YAW rotation 
    tp.data.operate.execute_equation(f"{{x}} = {{x}} * cos({alpha_rad}) - {{y}} * sin({alpha_rad})")
    tp.data.operate.execute_equation(f"{{y}} = {{x}} * sin({alpha_rad}) + {{y}} * cos({alpha_rad})")

    # Get Rotated
    return

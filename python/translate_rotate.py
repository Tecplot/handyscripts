"""
Given functions for translation and rotation in 2D and 3D.

"""

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import math
import numpy as np

def translate_to_XYZ(zone_num, new_x=0 , new_y=0, new_z=0, by_index_num = False, index_num = -1):
  """
  Params:
  zone - must supply the zone number
  new_x, new_y, new_z - should be set if setting new x,y,z coordinates.
  by_index_num - disregards new_x, new_y, new_z to set xyz by index instead.
  index_num - must be set if by_index_num = True
  """

  ds = tp.active_frame().dataset
  zone = ds.zone(zone_num)
  
  if by_index_num:
    # supply the zone and index you want to move to. 
    # Note that you can pick nearest node and therefore exact I, by using ctrl + click with the probe tool in Tecplot
    if index_num < 0:
       return print("\n", "Must supply valid node/cell index number to translate to...", "\n")

    
    new_x = ds.variable("x").values(zone)[index_num-1] # subtract 1 because Tecplot is 1-indexed, python is 0-indexed. 
    new_y = ds.variable("y").values(zone)[index_num-1]
    new_z = ds.variable("z").values(zone)[index_num-1]
     

  # translate to new XYZ
  tp.data.operate.execute_equation(equation=f"{{x}} = {{x}} - {new_x}")
  tp.data.operate.execute_equation(equation=f"{{y}} = {{y}} - {new_y}")
  tp.data.operate.execute_equation(equation=f"{{z}} = {{z}} - {new_z}")



def rotate_2D(theta, rotation_plane="xy"):
  """
  Params:
  theta - give in degree, made from reference axis, ex: XZ has X as the reference axis.
  rotation_plane - the plane you would like to rotate about, default is XY, but could be given as XZ, YZ, or some other var named axes.
  """
  ds = tp.active_frame().dataset
  var_ls = [var.name for var in ds.variables()]
  ref_axis = rotation_plane[0]
  terminal_axis = rotation_plane[1]

  if ref_axis and terminal_axis not in var_ls:
     return print("rotation vars not found in dataset")
  if len(rotation_plane) != 2:
     return print("invlaid rotation plane")
  
  theta_radian = np.radians(theta)
  # because equations are sequential, intermediate vars must be created.
  tp.data.operate.execute_equation(equation=f"{{new_ref_axis}} = {{{ref_axis}}} * cos({theta_radian}) + {{{terminal_axis}}}*sin({theta_radian})")
  tp.data.operate.execute_equation(equation=f"{{new_term_axis}} = {{{terminal_axis}}} * cos({theta_radian}) - {{{ref_axis}}}*sin({theta_radian})")

  tp.data.operate.execute_equation(equation=f"{{{ref_axis}}} = {{new_ref_axis}}")
  tp.data.operate.execute_equation(equation=f"{{{terminal_axis}}} = {{new_term_axis}}")
  
  #axes = tp.active_frame().plot().axes
  #axes.x_axis.variable = ds.variable('new_x')
  #axes.y_axis.variable = ds.variable('new_y')
  return


def arbitrary_xyz_rotation(alpha, beta, gamma):
    """  
    Currently only set up for cartesian coords with axis names xyz

    Params:
    Provide 3 angles in degrees
    
    General rotation matrices taken from https://en.wikipedia.org/wiki/Rotation_matrix
    Equations applied are a result of rotational matrix R @ [x,y,z] 
    where R = R_z @ R_y @ R_x

    yaw -> XY -> alpha
    pitch -> XZ -> βeta
    roll -> YZ -> gamma

                Z
                |
                |   
                |      
              β | γ 
               \|/   
                o---------- Y
               / \ 
              /   α
             /       
            X        
    """

    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)
    gamma_rad = np.radians(gamma)

    # Order matters! Matrix multiplication not commutative!
    # Resultant matrix of rotation R = R_z @ R_y @ R_x
    # R @ [x,y,z] gives the below equations. Because they are applied sequentially, new vars are created.

    # ds = tp.active_frame().dataset
    # var_ls = [var.name for var in ds.variables()]
    
    x_prime = f"cos({alpha_rad}) * cos({beta_rad}) * {{x}} + \
      (cos({alpha_rad}) * sin({beta_rad}) * sin({gamma_rad}) - sin({alpha_rad}) * cos({gamma_rad})) * {{y}} +  \
      (cos({alpha_rad}) * sin({beta_rad}) * cos({gamma_rad}) + sin({alpha_rad}) * sin({gamma_rad})) * {{z}}"

    y_prime = f"sin({alpha_rad}) * cos({beta_rad}) * {{x}} + \
      (sin({alpha_rad}) * sin({beta_rad}) * sin({gamma_rad}) + cos({alpha_rad}) * cos({gamma_rad})) * {{y}} + \
      (sin({alpha_rad}) * sin({beta_rad}) * cos({gamma_rad}) - cos({alpha_rad}) * sin({gamma_rad})) * {{z}}"

    z_prime = f"-sin({beta_rad}) * {{x}} + \
      cos({beta_rad}) * sin({gamma_rad}) * {{y}} + \
      cos({beta_rad}) * cos({gamma_rad}) * {{z}}"
    
    # new vars to behave as intermediate axes
    tp.data.operate.execute_equation(equation=f"{{x_new}} = {x_prime}")
    tp.data.operate.execute_equation(equation=f"{{y_new}} = {y_prime}")
    tp.data.operate.execute_equation(equation=f"{{z_new}} = {z_prime}")

    # Now set them back.
    tp.data.operate.execute_equation(equation="{x} = {x_new}")
    tp.data.operate.execute_equation(equation="{y} = {y_new}")
    tp.data.operate.execute_equation(equation="{z} = {z_new}")

    # Get Rotated
    return

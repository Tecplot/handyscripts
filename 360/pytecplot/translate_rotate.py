"""
Given functions for translation and rotation in 2D and 3D.

-- Example usage of arbitrary_xyz_rotation on some line in 3D space --

some_line_zone = tp.active_frame().dataset.zone(zone#)
x_component = some_line_zone.values('X')[0] - some_line_zone.values('X')[1]
y_component = some_line_zone.values('Y')[0] - some_line_zone.values('Y')[1]
z_component = some_line_zone.values('Z')[0] - some_line_zone.values('Z')[1]
direction_vector = np.array([x_component, y_component, z_component])
d_normalized = direction_vector / np.linalg.norm(direction_vector)

arbitrary_xyz_rotation(normal_vector=d_normalized)
-> data will be re-oriented along that line in space.
"""

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import numpy as np

def translate_to_XYZ(zone_num, new_x=0 , new_y=0, new_z=0, by_index_num = False, index_num = -1):
  """
  Params:
  zone - must supply the zone number
  new_x, new_y, new_z - should be set if setting new x,y,z coordinates.
  by_index_num - disregards new_x, new_y, new_z to set xyz by index instead.
  index_num - must be set if by_index_num = True
  """
  frame = tp.active_frame()
  plot = frame.plot()
  ds = frame.dataset
  zone = ds.zone(zone_num)
  var_ls = [var.name for var in ds.variables()]

  x_var = "x"
  y_var = "y"
  z_var = "z"

  try:
    x_var = plot.axes.x_axis.variable.name
    y_var = plot.axes.y_axis.variable.name
    z_var = plot.axes.z_axis.variable.name
  except AttributeError:
    pass

  if x_var not in var_ls or y_var not in var_ls or z_var not in var_ls:
    return print("translation vars not found in dataset")
  
  if by_index_num:
    # supply the zone and index you want to move to. 
    # Note that you can pick nearest node and therefore exact I, by using ctrl + click with the probe tool in Tecplot
    if index_num < 0:
       return print("\n", "Must supply valid node/cell index number to translate to...", "\n")

    
    new_x = ds.variable(x_var).values(zone)[index_num-1] # subtract 1 because Tecplot is 1-indexed, python is 0-indexed. 
    new_y = ds.variable(y_var).values(zone)[index_num-1]
    new_z = ds.variable(z_var).values(zone)[index_num-1]
     

  # translate to new XYZ
  tp.data.operate.execute_equation(equation=f"{{{x_var}}} = {{{x_var}}} - {new_x}")
  tp.data.operate.execute_equation(equation=f"{{{y_var}}} = {{{y_var}}} - {new_y}")
  tp.data.operate.execute_equation(equation=f"{{{z_var}}} = {{{z_var}}} - {new_z}")



def rotate_2D(theta, rotation_plane="xy"):
  """
  Params:
  theta - give in degree, made from reference axis, ex: XZ has X as the reference axis.
  rotation_plane - the plane you would like to rotate about, default is XY, but could be given as XZ, YZ, or some other var named axes.
  """
  frame = tp.active_frame()
  plot = frame.plot()
  ds = frame.dataset
  var_ls = [var.name for var in ds.variables()]
  axis_map = {}

  try:
     axis_map = {
        "x": plot.axes.x_axis.variable.name,
        "y": plot.axes.y_axis.variable.name,
        "z": plot.axes.z_axis.variable.name
     }
  except AttributeError:
     axis_map = {"x": "x", "y": "y", "z": "z"}

  ref_axis = axis_map.get(rotation_plane[0].lower(), rotation_plane[0])
  terminal_axis = axis_map.get(rotation_plane[1].lower(), rotation_plane[1])

  if ref_axis not in var_ls or terminal_axis not in var_ls:
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


def arbitrary_xyz_rotation(alpha=0, beta=0, gamma=0, normal_vector=None):
    r"""  
    Params:
    Provide 3 angles in degrees, or supply normal_vector=(nx, ny, nz).
    If normal_vector is supplied, it takes precedence over alpha/beta/gamma and
    constructs a right-handed basis whose z-axis is aligned with that direction.
    
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

    frame = tp.active_frame()
    plot = frame.plot()
    ds = frame.dataset
    var_ls = [var.name for var in ds.variables()]

    x_var = "x"
    y_var = "y"
    z_var = "z"

    try:
        x_var = plot.axes.x_axis.variable.name
        y_var = plot.axes.y_axis.variable.name
        z_var = plot.axes.z_axis.variable.name
    except AttributeError:
        pass

    if x_var not in var_ls or y_var not in var_ls or z_var not in var_ls:
        return print("rotation vars not found in dataset")

    def build_linear_expr(coeffs):
        terms = []
        axis_vars = (x_var, y_var, z_var)

        for coeff, axis_var in zip(coeffs, axis_vars):
            if np.isclose(coeff, 0.0):
                coeff = 0.0
            terms.append(f"({coeff}) * {{{axis_var}}}")

        return " + ".join(terms)

    if normal_vector is not None:
        z_axis = np.asarray(normal_vector, dtype=float).reshape(-1)
        if z_axis.size != 3:
            return print("normal_vector must contain exactly 3 values")

        z_axis_norm = np.linalg.norm(z_axis)
        if np.isclose(z_axis_norm, 0.0):
            return print("normal_vector must be non-zero")
        z_axis = z_axis / z_axis_norm

        ref_axis = np.array([0.0, 0.0, 1.0])
        if np.isclose(abs(np.dot(z_axis, ref_axis)), 1.0):
            ref_axis = np.array([0.0, 1.0, 0.0])

        x_axis = np.cross(ref_axis, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)

        # Re-express coordinates in a basis whose +z axis points along the
        # supplied direction vector.
        x_prime = build_linear_expr(x_axis)
        y_prime = build_linear_expr(y_axis)
        z_prime = build_linear_expr(z_axis)
    else:
        alpha_rad = np.radians(alpha)
        beta_rad = np.radians(beta)
        gamma_rad = np.radians(gamma)

        # Order matters! Matrix multiplication not commutative!
        # Resultant matrix of rotation R = R_z @ R_y @ R_x
        # R @ [x,y,z] gives the below equations. Because they are applied sequentially, new vars are created.
        
        x_prime = f"cos({alpha_rad}) * cos({beta_rad}) * {{{x_var}}} + \
          (cos({alpha_rad}) * sin({beta_rad}) * sin({gamma_rad}) - sin({alpha_rad}) * cos({gamma_rad})) * {{{y_var}}} +  \
          (cos({alpha_rad}) * sin({beta_rad}) * cos({gamma_rad}) + sin({alpha_rad}) * sin({gamma_rad})) * {{{z_var}}}"

        y_prime = f"sin({alpha_rad}) * cos({beta_rad}) * {{{x_var}}} + \
          (sin({alpha_rad}) * sin({beta_rad}) * sin({gamma_rad}) + cos({alpha_rad}) * cos({gamma_rad})) * {{{y_var}}} + \
          (sin({alpha_rad}) * sin({beta_rad}) * cos({gamma_rad}) - cos({alpha_rad}) * sin({gamma_rad})) * {{{z_var}}}"

        z_prime = f"-sin({beta_rad}) * {{{x_var}}} + \
          cos({beta_rad}) * sin({gamma_rad}) * {{{y_var}}} + \
          cos({beta_rad}) * cos({gamma_rad}) * {{{z_var}}}"
    
    # new vars to behave as intermediate axes
    tp.data.operate.execute_equation(equation=f"{{x_new}} = {x_prime}")
    tp.data.operate.execute_equation(equation=f"{{y_new}} = {y_prime}")
    tp.data.operate.execute_equation(equation=f"{{z_new}} = {z_prime}")

    # Now set them back.
    tp.data.operate.execute_equation(equation=f"{{{x_var}}} = {{x_new}}")
    tp.data.operate.execute_equation(equation=f"{{{y_var}}} = {{y_new}}")
    tp.data.operate.execute_equation(equation=f"{{{z_var}}} = {{z_new}}")

    # Get Rotated
    return

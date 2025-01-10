"""
This script outputs courant number as a variable for the given zone.

The Courant number is a non-dimensional number named after the mathematician Richard Courant. 
The Courant number can be used in Computational Fluid Dynamics (CFD) simulations 
to evaluate the time step requirements of a transient simulation for a given mesh size and flow velocity 
and is linked to the Courant Friedrichs Lewy (CFL) stability condition of numerical schemes.

source: https://sim-flow.com/courant-number-in-cfd/

For 2D axis-aligned cases, below courant calculation will yield 0 due to dot product, seek "simple_courant_number_calculation.py" script

We seek a general formulation of the Courant number to work in all structured CFD cases, 
therefore the equation below:

C = (1/2)Δt * (|U_i * n_f| * A_f) / V

U_i - represents velocity in given flow direction
n_f - Represents the face-normal, that is, normal of the face, 
pointing to the centroid of the cell.
∆t - representative time step of the simulation. 
Here, simple average is used.
V - length/area/volume of cell.

We expect the sum of all normals facing the cell centroid to be 0, 
therefore the magnitude of the inner product of A * n is used.
This results in double the desired result, 
therefore we introduce the 1/2 constant.
"""

import math
import numpy as np
import tecplot as tp
from tecplot.constant import *
import time

# tp.data.load_tecplot('/path/to/dataset.plt')

tp.session.connect()
ds = tp.active_frame().dataset

ZONE_NUMBER = 1
VELOCITY_VAR_NAME = 'VelocityVec_X'


class DefineFEGeom:
    def __init__(self, coords):
        """
        params:
        takes a set of x,y,z coords that define given FE element. 
        get_geom_area_vectors passes zone-type to other functions, 
        to return desired face-areas.

        The compute_face_areas function describes how areas are calcuated 
        and should be referred to for questions regarding results.
        """
        self.coords = coords

    
    def calculate_vectors(self, vertices, vector_pairs):
        """
        Calculate vectors based on vertex pairs.
        """
        return {
            pair: np.subtract(vertices[pair[1]], vertices[pair[0]]) for pair in vector_pairs
        }


    def compute_face_areas(self, faces, vectors):
        """ 
        We expect that 2D FE elements will pass a single face and return a single result.

        Returns: 
        Dict of face areas and magnitude.

        Notes: 
        Magnitude area-vector == normal vector of parallelogram defined by face.
        Cross product is used to define face-area, this implicitly assumes parallelogram.
        This assumption means the more irregular faces are, the less accurate this method is.
        """
        result = {}
        for face, (_, edges) in faces.items():
            v1 = vectors[edges[0]]
            v2 = vectors[edges[1]]
            area_vector = np.cross(v1, v2)
            magnitude = np.linalg.norm(area_vector)
            result[face] = (area_vector, magnitude)
        return result


    def fe_mixed(self):
        number_verts = len(self.coords)
        if number_verts == 3:
            return self.fe_triangle()
        elif number_verts == 4:
            return self.fe_quad()
        elif number_verts == 8:
            return self.fe_brick()
        else:
            return self.fe_tetra()
        

    def fe_triangle(self):
        """
        Define geometry for an FETriangle zone type.
        """
        # Extract the vertices for the triangle
        vertices = {
            'n1': np.array(self.coords[0]),
            'n2': np.array(self.coords[1]),
            'n3': np.array(self.coords[2]),
        }

        # Define vector pairs to form the edges of the triangle
        vector_pairs = [
            ('n1', 'n2'), ('n1', 'n3')
        ]

        # Calculate the edge vectors
        vectors = self.calculate_vectors(vertices, vector_pairs)

        # Compute the area vector using the cross product of two edges
        area_vector = np.cross(vectors[('n1', 'n2')], vectors[('n1', 'n3')])
        area = 0.5 * np.linalg.norm(area_vector)  # Triangle area is half the magnitude of the area vector
        return {"face": (area_vector, area)}


    def fe_tetra(self):
        """
        Define geometry for an FETetrahedron zone type.
        """
        vertices = {
            'n1': np.array(self.coords[0]),
            'n2': np.array(self.coords[1]),
            'n3': np.array(self.coords[2]),
            'n4': np.array(self.coords[3])
        }

        vector_pairs = [
            ('n1', 'n2'), 
            ('n1', 'n3'),
            ('n1', 'n4'),
            ('n2', 'n3'),
            ('n2', 'n4'),
            ('n3', 'n4')
        ]

        # All necessary edges, we define with vector pair.
        vectors = self.calculate_vectors(vertices, vector_pairs)

        faces = {
            "Face1": (['n1', 'n2', 'n3'], [('n1', 'n2'), ('n1', 'n3')]),
            "Face2": (['n1', 'n2', 'n4'], [('n1', 'n2'), ('n1', 'n4')]),
            "Face3": (['n1', 'n3', 'n4'], [('n1', 'n3'), ('n1', 'n4')]),
            "Face4": (['n2', 'n3', 'n4'], [('n2', 'n3'), ('n2', 'n4')])
        }

        return self.compute_face_areas(faces, vectors)


    def fe_brick(self):
        """
        Define geometry for an FEBrick zone type.
        """
        vertices = {
            'n1': np.array(self.coords[0]), 
            'n2': np.array(self.coords[1]), 
            'n3': np.array(self.coords[2]), 
            'n4': np.array(self.coords[3]),
            'n5': np.array(self.coords[4]), 
            'n6': np.array(self.coords[5]), 
            'n7': np.array(self.coords[6]), 
            'n8': np.array(self.coords[7])
        }

        vector_pairs = [
            ('n1', 'n2'), 
            ('n1', 'n4'), 
            ('n2', 'n3'), 
            ('n3', 'n4'),
            ('n5', 'n6'), 
            ('n5', 'n8'), 
            ('n6', 'n7'), 
            ('n7', 'n8'),
            ('n1', 'n5'), 
            ('n2', 'n6'), 
            ('n3', 'n7'), 
            ('n4', 'n8')
        ]
        
        # All necessary edges, we define with vector pair.
        vectors = self.calculate_vectors(vertices, vector_pairs)

        faces = {
            "Bottom": (['n1', 'n2', 'n3', 'n4'], [('n1', 'n2'), ('n1', 'n4')]),
            "Top": (['n5', 'n6', 'n7', 'n8'], [('n5', 'n6'), ('n5', 'n8')]),
            "Front": (['n1', 'n2', 'n6', 'n5'], [('n1', 'n2'), ('n1', 'n5')]),
            "Back": (['n3', 'n4', 'n8', 'n7'], [('n3', 'n4'), ('n3', 'n7')]),
            "Left": (['n1', 'n4', 'n8', 'n5'], [('n1', 'n4'), ('n1', 'n5')]),
            "Right": (['n2', 'n3', 'n7', 'n6'], [('n2', 'n3'), ('n2', 'n6')])
        }

        return self.compute_face_areas(faces, vectors)


    def fe_quad(self):
        """
        Define geometry for an FEQuad zone type.
        """
        vertices = {
            'n1': np.array(self.coords[0]),
            'n2': np.array(self.coords[1]),
            'n3': np.array(self.coords[2]),
            'n4': np.array(self.coords[3])
        }

        vector_pairs = [
            ('n1', 'n2'), ('n1', 'n4')
        ]
        
        vectors = self.calculate_vectors(vertices, vector_pairs)

        area_vector = np.cross(vectors[('n1', 'n2')], vectors[('n1', 'n4')])
        area = np.linalg.norm(area_vector)

        return {"face": (area_vector, area)}


    def get_geom_area_vectors(self, zone_type):
        """
        Main function to compute geometry based on the zone type.
        """
        if zone_type == ZoneType.FEBrick:
            return self.fe_brick()
        elif zone_type == ZoneType.FETetra:
            return self.fe_tetra()
        elif zone_type == ZoneType.FEQuad:
            return self.fe_quad()
        elif zone_type == ZoneType.FETriangle:
            return self.fe_triangle()
        elif zone_type == ZoneType.FEMixed:
            return self.fe_mixed()
        else:
            print(f"Zone type {zone_type} has not been defined for this script.")
            return


def get_cell_volume_var():
    """
    Checks for cell volume var.
    """
    if not list(ds.variables('cell volume')):
        print("calculating cell volume variable")
        tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
            command="Calculate Function='CELLVOLUME' Normalization='None' ValueLocation='Nodal' CalculateOnDemand='F' UseMorePointsForFEGradientCalculations='F'")
    return


def get_representative_time_step():
    solution_times = set([zone.solution_time for zone in ds.zones()])
    #print(len(solution_times), max(solution_times), min(solution_times))
    return (max(solution_times) - min(solution_times)) / len(solution_times)


def get_all_vars_as_nodal(zone, velocity_var_name):
    x = zone.values('X')
    y = zone.values('Y')
    z = zone.values('Z')
    U = zone.values(velocity_var_name)
    CELL_VOLUME = zone.values('cell volume')
    
    x_loc = x.location
    y_loc = y.location
    z_loc = z.location
    u_loc = U.location
    cell_vol_loc = CELL_VOLUME.location

    var_set = {
        "X": x,
        "Y": y,
        "Z": z,
        velocity_var_name: U, 
        "Cell Volume": CELL_VOLUME
    }

    all_var_names = [var.name for var in ds.variables()]
    for var_name, var_location in zip(var_set.keys(), [x_loc,y_loc,z_loc,u_loc,cell_vol_loc]):
        if var_location == tp.constant.ValueLocation.Nodal:
            continue
        
        else:
            # if no nodal var exists, we must make it
            print(f"Variable {var_name} is cell-centered, creating nodal version for calculation", "\n")
            tp.data.operate.execute_equation(f"{{{var_name}_Nodal}} = {{{var_name}}}",
                                             zones=[zone],
                                             value_location=tp.constant.ValueLocation.Nodal)
            
            var_set[var_name] = zone.values(f'{var_name}_Nodal')
        
    return var_set


def calculate_courant_number_for_zone(zone, velocity_var_name: str, manually_set_timestep=False):
    """
    Params:
    zone - supply zone number
    velocity_var_name - give the name of your velocity variable in Tecplot
    manually_set_timestep - enter timestep here if you wish to manually input a value, 
    defaults to false. 
    
    Overview:
    Given zonetype, i.e. FEBrick, we then need to define each face, 
    which means we need to look at connectivity. 
    Ex: FEBrick is defined like so:
    
        n6---------n7
       / |        / |
      /  |       /  |
    n5---------n8   |
     |   |      |   |
     |   n2-----|---n3
     |  /       |  /
     | /        | /
    n1----------n4
    """
    if manually_set_timestep:
        timestep = manually_set_timestep
    else:
        timestep = get_representative_time_step()
    
    if timestep == 0:
        print(f"timestep is {timestep} for simulation, courant number will be 0. Is this data transient?")
        return
        
    zone_type = zone.zone_type
    get_cell_volume_var()
    var_set = get_all_vars_as_nodal(zone, velocity_var_name)
    
    print(f"number of elements: {zone.num_elements}")
    start = time.time()
    x = var_set['X'].as_numpy_array()
    y = var_set['Y'].as_numpy_array()
    z = var_set['Z'].as_numpy_array()
    xyz_data = np.stack((x,y,z), axis=1)
    u = var_set[velocity_var_name].as_numpy_array()
    cell_vol = var_set['Cell Volume'].as_numpy_array()

    if not list(ds.variables('Courant number')):
        ds.add_variable('Courant number', locations=ValueLocation.Nodal)
    zone.values('Courant number')[:] = [0 for _ in range(len(zone.values('Courant number')[:]))]
    
    start = time.time()
    with tp.session.suspend():
        print("calculating Courant number on each element.")
        checkpoint_nums = [math.floor(zone.num_elements / 10) * i for i in range(0,9)]
        for element in range(1350, zone.num_elements-63783):
            original_element_num = element          
            if zone_type == ZoneType.FEMixed:
                # for FE-Mixed, retrieve the element number from the section which contains the element. 
                # This is needed because the "element" number reverts back to 0 for new each nodemapsection.
                nodemap_section = zone.nodemap.section_element(element)
                element = nodemap_section[1]
                nmap = zone.nodemap.nodes(element, section=nodemap_section[0])
            else:
                # nodemap access is different for FEClassicNodemap object
                nmap = np.array(zone.nodemap[element])
            nmap_coords = xyz_data[nmap]
            u_node = u[nmap[0]]
            node_cell_vol = cell_vol[nmap[0]]
                         
            cell_geom = DefineFEGeom(nmap_coords)
            area_vectors = cell_geom.get_geom_area_vectors(zone_type=zone_type)

            courant_number_on_each_face = [calculate_courant_number(timestep, u_node, normal, area, node_cell_vol) for normal, area in area_vectors.values()]
            total_courant_number = sum(courant_number_on_each_face)
            zone.values('Courant number')[nmap[0]] = total_courant_number
            
            if original_element_num in checkpoint_nums:
                print(f"On cell {original_element_num + 1} out of ~{zone.num_elements}")
                print(f"time since calculation start: {round(time.time() - start, 2)}", "\n")
            if original_element_num == zone.num_elements-1:
                finish = time.time()
                print(f"time taken: {round(finish - start, 2)}")

    tp.session.clear_suspend()


def calculate_courant_number(t, U, n, A, V):
    U_vector = [U, 0, 0]
    print(U_vector)
    mag_U_dot_n = abs(np.dot(U_vector, n))
    print(mag_U_dot_n)
    return ((0.5)*t*mag_U_dot_n*A / V)


calculate_courant_number_for_zone(ds.zone(ZONE_NUMBER), VELOCITY_VAR_NAME)


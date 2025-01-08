"""
This script outputs courant number as a variable for the given zone.

The Courant number is a non-dimensional number named after the mathematician Richard Courant. 
The Courant number can be used in Computational Fluid Dynamics (CFD) simulations 
to evaluate the time step requirements of a transient simulation for a given mesh size and flow velocity 
and is linked to the Courant Friedrichs Lewy (CFL) stability condition of numerical schemes.

source: https://sim-flow.com/courant-number-in-cfd/

We seek a general formulation of the Courant number to work in all structured CFD cases, 
therefore the equation below is used for dimension i, with corresponding velocity U_i:
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

ZONE_NUMBER = 11
VELOCITY_VAR_NAME = 'VelocityX'


class DefineFEGeom:
    def __init__(self, x: list, y: list, z: list):
        """
        params:
        takes a set of x,y,z coords that define given FE element. 
        get_geom_area_vectors passes zone-type to other functions, 
        to return desired face-areas.

        The compute_face_areas function describes how areas are calcuated 
        and should be referred to for questions regarding results.
        """
        self.coords = list(zip(x, y, z))

    
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
        elif zone_type == ZoneType.FEQuad:
            return self.fe_quad()
        else:
            print(f"Zone type {zone_type} has not been defined for this script.")
            return



def get_cell_volume():
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


def calculate_courant_number_for_zone(zone, velocity_var_name: str):
    """
    Need to check that cell vol is in dataset and that all vars used are nodal, so that values are stored as if nodal.
    
    Given zonetype, i.e. FEBrick, we then need to define each face, 
    which means we need to look at connectivity. FEBrick is defined like so:
    
        n6---------n7
       / |        / |
      /  |       /  |
    n5---------n8   |
     |   |      |   |
     |   n2-----|---n3
     |  /       |  /
     | /        | /
    n1----------n4
    
    So long as elements are defined squentially in exactly the same order,  we can compute the needed values.
    """
    timestep = get_representative_time_step()
    if timestep == 0:
        print(f"time step is {timestep} for simulation, courant number will be 0. Is this data transient?")
        return
    
    zone_type = zone.zone_type
    get_cell_volume()
    x = zone.values('X')[:]
    y = zone.values('Y')[:]
    z = zone.values('Z')[:]
    U = zone.values(velocity_var_name)[:]
    CELL_VOLUME = zone.values('cell volume')[:]

    if not list(ds.variables('courant number')):
        ds.add_variable('courant number')
    
    print(f"number of elements: {zone.num_elements}")
    start = time.time()

    for cell_index in range(zone.num_elements):
        
        nodemap = zone.nodemap[cell_index]
        x_nodemap = [x[i] for i in nodemap]
        y_nodemap = [y[i] for i in nodemap]
        z_nodemap = [z[i] for i in nodemap]
        U_node = U[cell_index]
        cell_vol = CELL_VOLUME[cell_index]
        
        cell_geom = DefineFEGeom(x_nodemap, y_nodemap, z_nodemap)
        area_vectors = cell_geom.get_geom_area_vectors(zone_type=zone_type)
        courant_number_on_each_face = [calculate_courant_number(timestep, U_node, normal, area, cell_vol) for normal, area in area_vectors.values()]
        total_courant_number = sum(courant_number_on_each_face)
        zone.values('courant number')[cell_index] = total_courant_number

        checkpoint_nums = [math.floor(zone.num_elements / 10) * i for i in range(0,9)]
        if cell_index in checkpoint_nums:
            print(f"cell index is on {cell_index + 1} out of ~{zone.num_elements}")
            print(f"time since calculation start: {round(time.time() - start, 2)}", "\n")
        if cell_index == zone.num_elements-1:
            finish = time.time()
            print(f"time taken: {round(finish - start, 2)}")
    

def calculate_courant_number(t, U, n, A, V):
    U_vector = [U, 0, 0]
    mag_U_dot_n = abs(np.dot(U_vector, n))
    return ((0.5)*t*mag_U_dot_n*A / V)


def define_geom_area_vectors(x: list,y: list,z: list, zone_type):
    """
    chatGPT was used to optimize this and make it as fast as pythonically possible :)
    Returns dict of form:
    Face: (normal_vector, area)

    Notes: 
    magnitude of area vector == area
    algorithm implicitly assumes that the FE element is a parallelogram,
    This makes highly skewed faces inaccurate.
    """
    coords = list(zip(x,y,z))
    result = {}

    if zone_type == ZoneType.FEBrick:
        # Define vertices as numpy arrays for performance
        vertices = {
            'n1': np.array(coords[0]), 
            'n2': np.array(coords[1]), 
            'n3': np.array(coords[2]), 
            'n4': np.array(coords[3]),
            'n5': np.array(coords[4]), 
            'n6': np.array(coords[5]), 
            'n7': np.array(coords[6]), 
            'n8': np.array(coords[7])
        }
        
        # Define the vectors between relevant vertices
        vectors = {
            ('n1', 'n2'): np.subtract(vertices['n2'], vertices['n1']),
            ('n1', 'n4'): np.subtract(vertices['n4'], vertices['n1']),
            ('n2', 'n3'): np.subtract(vertices['n3'], vertices['n2']),
            ('n3', 'n4'): np.subtract(vertices['n4'], vertices['n3']),
            ('n5', 'n6'): np.subtract(vertices['n6'], vertices['n5']),
            ('n5', 'n8'): np.subtract(vertices['n8'], vertices['n5']),
            ('n6', 'n7'): np.subtract(vertices['n7'], vertices['n6']),
            ('n7', 'n8'): np.subtract(vertices['n8'], vertices['n7']),
            ('n1', 'n5'): np.subtract(vertices['n5'], vertices['n1']),
            ('n2', 'n6'): np.subtract(vertices['n6'], vertices['n2']),
            ('n3', 'n7'): np.subtract(vertices['n7'], vertices['n3']),
            ('n4', 'n8'): np.subtract(vertices['n8'], vertices['n4'])
        }

        # Predefine face vertices and corresponding edges that define them
        faces = {
            "Bottom": (['n1', 'n2', 'n3', 'n4'], [('n1', 'n2'), ('n1', 'n4')]),
            "Top": (['n5', 'n6', 'n7', 'n8'], [('n5', 'n6'), ('n5', 'n8')]),
            "Front": (['n1', 'n2', 'n6', 'n5'], [('n1', 'n2'), ('n1', 'n5')]),
            "Back": (['n3', 'n4', 'n8', 'n7'], [('n3', 'n4'), ('n3', 'n7')]),
            "Left": (['n1', 'n4', 'n8', 'n5'], [('n1', 'n4'), ('n1', 'n5')]),
            "Right": (['n2', 'n3', 'n7', 'n6'], [('n2', 'n3'), ('n2', 'n6')])
        }
        
        # We get area vector A, which has magnitude of area and direction of normal vector
        # We are able to use lengths already calculated, and only need to calculate cross-product
        for face, (verts, edges) in faces.items():

            # No computation, only reference to precomputed vector defn.
            v1 = vectors[edges[0]] 
            v2 = vectors[edges[1]]

            # magnitude of area vector == area of parallelogram defined by v1,v2
            area_vector = np.cross(v1, v2)
            magnitude = np.linalg.norm(area_vector)
            result[face] = (area_vector, magnitude)
        return result
    
    elif zone_type == ZoneType.FEQuad:
        vertices = {
            'n1': np.array(coords[0]), 
            'n2': np.array(coords[1]), 
            'n3': np.array(coords[2]), 
            'n4': np.array(coords[3])
        }

        vectors = {
            ('n1', 'n2'): np.subtract(vertices['n2'], vertices['n1']),
            ('n1', 'n4'): np.subtract(vertices['n4'], vertices['n1'])
        }

        # there is only one face... making this easier.
        area_vector = np.cross(vectors[('n1', 'n2')], vectors[('n1', 'n4')])
        area = np.linalg.norm(area_vector)
        result["face"] = (area_vector, area)

        return result
    
    
    else:
        print(f"zone type {zone_type} has not been defined for this script")
        return


calculate_courant_number_for_zone(ds.zone(ZONE_NUMBER), VELOCITY_VAR_NAME)














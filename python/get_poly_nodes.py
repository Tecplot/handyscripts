import time
import os
import tecplot  as tp
from tecplot.data.facemap import Elementmap

def element_nodes(zone, element):
    face_map = zone.facemap
    element_map = Elementmap(zone)
    unique_element_nodes = set()
    for face in element_map.faces(element):
        num_nodes = face_map.num_nodes(face=face) # Global face numbers, don't supply and element
        for node_offset in range(num_nodes):
            node = face_map.node(face, node_offset) # Global face numbers, don't supply and element
            unique_element_nodes.add(node)
    return unique_element_nodes

def get_nodes(node_map, element):
    assert(element < len(node_map))
    return node_map[element]

def get_node_index(node_map, element, corner):
    assert(element < len(node_map))
    assert(corner < len(node_map[element]))
    return node_map[element][corner]

tp.new_layout()
examples_dir = tp.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
tp.load_layout(infile)

ds = tp.active_frame().dataset

zone = ds.zone(0)
print(zone)

now = time.time()
# Create a node map for the polyhedral (or polygonal) zone
node_map = dict()
for element in range(zone.num_elements):
    unique_nodes = list(element_nodes(zone, element))
    node_map[element] = unique_nodes
print("Create node map time:", time.time()-now)

# Use the node map to get the node at a specific corner.  Poly data can have an arbitrary
# number of 'corners', so make sure you don't use too large a corner number for the element
element = 10
unique_nodes = get_nodes(node_map, element)
num_corners = len(unique_nodes)
print("All numbers are zero-based!!!")
for corner in range(num_corners):
    node = get_node_index(node_map, element, corner)
    print(f"Element: {element}, Corner: {corner}, Node: {node}")


import tecplot as tp
from tecplot.constant import *


def setup_base_FEZone():
    inputmatrix = (
        (1, 1, 0.5, 7),
        (0, 0, 0, 4),
        (3, 3, 1, 9),
        (2, 2, 0.5, 8),
    )

    # Connectivity list
    conn = ((1, 0), (0, 3), (3, 2))  # In order this would be [1,0,3,2]

    # Setup dataset and zone
    ds = tp.active_frame().create_dataset('Data', ['x', 'y', 'f', 's'])
    z = ds.add_fe_zone(ZoneType.FELineSeg,
                       name='FE Line',
                       num_points=len(inputmatrix), num_elements=len(conn))

    # Populate zone values from input matrix.
    z.values('x')[:] = [n[0] for n in inputmatrix]
    z.values('y')[:] = [n[1] for n in inputmatrix]
    z.values('f')[:] = [n[2] for n in inputmatrix]
    z.values('s')[:] = [n[3] for n in inputmatrix]

    # Setup Connectivity
    z.nodemap[:] = conn
    return ds


def feLineSeg_to_ordered(fezone):
    print(fezone.zone_type)
    if fezone.zone_type == tp.constant.ZoneType.FELineSeg:
        print("Num Elements: ", fezone.num_elements)
        nodes = fezone.nodemap
        print("Nodemap: ", [n for n in nodes])

        # Convert to I ordered zone
        continue_line = True
        index_list = [nodes[0][0]]  # Seed with first value in list
        cur_cell = 0
        # need lists not tuples (at least for nodes_R):
        nodes_L = list(list(zip(*nodes))[0])  # Transform nodes and only look at "left side"
        nodes_R = list(list(zip(*nodes))[1])  # Transform nodes and only look at "right side"
        print("nodes_L: ", nodes_L)
        print("nodes_R: ", nodes_R)

        while continue_line:
            nextnode = nodes_R[cur_cell]  # Get the next RHS at the index defined by the last index
            index_list.append(nextnode)  # Add the next value into the point list
            
            nodes_R[cur_cell] = 'x'  # x index out to get second appearance if node idx exists twice on RHS.
            print("nextnode: ", nextnode)
            
            if nextnode in nodes_L:
                cur_cell = nodes_L.index(nextnode)
            else:
                if nextnode in nodes_R:  # look for second appearance of node index on RHS. That's why the 'x' has been set.
                    cur_cell = nodes_R.index(nextnode)   
                    nodes_L[cur_cell], nodes_R[cur_cell] = nodes_R[cur_cell],nodes_L[cur_cell]
                else:
                # Stops if no LHS of the coorisponds to the RSH, this happens if the line is not a loop.
                    continue_line = False

            if nextnode == nodes_L[0]:  # If line is a loop stop.
                continue_line = False

        #print("nodes_L: ", nodes_L)
        #print("nodes_R: ", nodes_R)               
        print("index list: ", index_list)
        print()
        
        ordered_out = ds.add_ordered_zone(fezone.name, len(index_list))
        
        for var in range(fezone.num_variables):  # For all variables
            # Get read/writeable access for specific Zone-Variable
            FE_vals = fezone.values(var)
            ordered_vals = ordered_out.values(var)

            ordered_idx = 0
            for FE_idx in index_list:
                # Overwrite the values of the ordered zone
                ordered_vals[ordered_idx] = FE_vals[FE_idx]
                ordered_idx += 1

    else:
        return False


# Use generated sample FEZone
ds = setup_base_FEZone()

# Extracted from slice of onera see "Extracting Slice" Pytecplot Example

init_zones = list(ds.zones())
for z in init_zones:
    # Convert
    feLineSeg_to_ordered(z)

ds.delete_zones(init_zones)
tp.data.save_tecplot_ascii('extract_ordered.dat', use_point_format=True)

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


def feLineSeg_to_ordered(fezone, ordered_out):
    print(fezone.zone_type)
    if fezone.zone_type == tp.constant.ZoneType.FELineSeg:
        print("Num Elements: ", fezone.num_elements)
        nodes = fezone.nodemap
        print("Nodemap: ", [n for n in nodes])

        # Convert to I ordered zone
        continue_line = True
        index_list = [nodes[0][0]]  # Seed with first value in list
        cur_index = 0
        nodes_T = map(list, zip(*nodes))[0]  # Transform nodes and only look at "left side"
        print("Left hand side of Nodemap: ", nodes_T)

        while continue_line:
            nextval = nodes[cur_index][1]  # Get the next RHS at the index defined by the last index

            index_list.append(nextval)  # Add the next value into the point list
            print(nextval)
            try:
                cur_index = nodes_T.index(nextval)  # Get the index of the next left hand side value
            except:
                # Stops if no LHS of the coorisponds to the RSH, this happens if the line is not a loop.
                continue_line = False

            if nextval == nodes[0][0]:  # If line is a loop stop.
                continue_line = False

        print(index_list)
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
    # Setup a new zone with the same dimension as the FE Line zone
    ordered_zone = ds.add_ordered_zone(z.name, z.num_points)
    # Convert
    feLineSeg_to_ordered(z, ordered_zone)

ds.delete_zones(init_zones)
tp.data.save_tecplot_ascii('extract_ordered.dat', use_point_format=True)

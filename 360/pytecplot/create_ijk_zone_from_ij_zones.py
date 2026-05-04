import numpy as np
import tecplot as tp
            
def create_ijk_zone_from_ij_zones(source_zones):
    """
    Creates a single IJK-Ordered zone from a list of IJ-Ordered zones.
    All source_zones must have the same IJ dimensions.
    
    source_zones - a list of IJ-Ordered zones, all of which have the same IJ dimensions.
    returns - A Zone which is IJK-Ordered
    """
    # Ensure source_zones is a list, just in case a generator is passed in
    source_zones = list(source_zones)

    with tp.session.suspend():
        ds = tp.active_frame().dataset
        
        IMax,JMax,KMax = source_zones[0].dimensions
        KMax = len(source_zones)

        dest_zone = ds.add_ordered_zone("Combined", (IMax,JMax,KMax))

    with tp.session.suspend():
        for v in ds.variables():
            # Collect the variable values from all the source zones
            vals = source_zones[0].values(v).as_numpy_array()
            for index in range(1,len(source_zones)):
                z = source_zones[index]
                vals = np.vstack((vals, z.values(v).as_numpy_array()))

            # Stuff the values into the destination zone
            dest_zone.values(v)[:] = vals

if __name__ == "__main__":
    # Example usage
    tp.session.connect()
    ds = tp.active_frame().dataset
    source_zones = list(ds.zones())
    new_zone = create_ijk_zone_from_ij_zones(source_zones)
    # Do something with new_zone


import time
import numpy as np
import tecplot as tp
            
def combine_structured_zones(source_zones):
    start = time.time()
    with tp.session.suspend():
        ds = tp.active_frame().dataset
        print(f"combining the following zones: {[zone.name for zone in source_zones]}")
        
        IMax,JMax,KMax = source_zones[0].dimensions
        KMax = len(source_zones)

        dest_zone = ds.add_ordered_zone("Combined", (IMax,JMax,KMax))

    with tp.session.suspend():
        for v in ds.variables():
            vals = source_zones[0].values(v).as_numpy_array()
            for index in range(1,len(source_zones)):
                z = source_zones[index]
                vals = np.vstack((vals, z.values(v).as_numpy_array()))
            dest_zone.values(v)[:] = vals
    print("Elapsed: ", time.time()-start)

tp.session.connect()

ds = tp.active_frame().dataset
source_zones = list(ds.zones())
combine_structured_zones(source_zones)


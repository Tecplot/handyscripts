import tecplot as tp

ds = tp.active_page().add_frame().create_dataset('D', ['x','y','z'])
z = ds.add_ordered_zone('Z1', (3,3,3))
zcopy = z.copy(i_range=(1, -1, 2))

import tecplot as tp

ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
z = ds.add_ordered_zone('Z1', (3,))
assert not z.values(0).passive

import tecplot as tp
frame = tp.active_frame()
dataset = frame.create_dataset('Dataset', ['x'])
dataset.add_ordered_zone('Zone', (3,3,3))
x = dataset.zone('Zone').values('x')
# allocate array using Python's ctypes
x_array = (x.c_type * len(x))()
# copy values from Dataset into ctypes array
x_array[:] = x[:]

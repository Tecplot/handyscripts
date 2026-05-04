import tecplot as tp

tp.new_layout()
frame = tp.active_frame()
dataset = frame.create_dataset('Dataset', ['x'])
dataset.add_ordered_zone('Zone', (2, 2, 2))
x = dataset.zone('Zone').values('x')

# loop over array copying out 4 values at a time
for i, offset in enumerate(range(0, len(x), 4)):
    x_array = x.copy(offset, 4)
    x_array[:] = [i] * 4
    x[offset:offset + 4] = x_array

# will print: [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
print(x[:])

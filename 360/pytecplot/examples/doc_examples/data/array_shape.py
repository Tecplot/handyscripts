import numpy as np
import tecplot as tp

frame = tp.active_frame()
dataset = frame.create_dataset('Dataset', ['X'])
zone = dataset.add_ordered_zone('Zone', shape=(3,3,3))

'''
the following will print:
[ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
'''
x = np.array(zone.values('X')[:])
print(x)

'''
the following will print:
[[[ 0.  0.  0.]
  [ 0.  0.  0.]
  [ 0.  0.  0.]]

 [[ 0.  0.  0.]
  [ 0.  0.  0.]
  [ 0.  0.  0.]]

 [[ 0.  0.  0.]
  [ 0.  0.  0.]
  [ 0.  0.  0.]]]
'''
#{DOC:highlight}[
x.shape = zone.values('X').shape
#]
print(x)

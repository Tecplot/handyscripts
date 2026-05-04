import tecplot

frame = tecplot.active_frame()
frame.name = '3D Data View'

# will print: "this frame: 3D Data View"
print('this frame:', frame.name)

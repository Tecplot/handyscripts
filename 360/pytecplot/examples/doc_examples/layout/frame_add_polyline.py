import tecplot

points = [ [1, 2,  3],
           [2, 4,  9],
           [3, 8, 27], ]

frame = tecplot.active_frame()
polyline = frame.add_polyline(points)

import tecplot

# print name of all frames on all pages
for frame in tecplot.frames():
    print(frame.name)

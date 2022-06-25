import tecplot

page = tecplot.active_page()
page.add_frame()  # create a second frame

# iterate over all frames and print their names
for frame in page.frames():
    print(frame.name)

# store a persistent list of frames
frames = page.frames()

# prints: ['Frame 001', 'Frame 002']
print([f.name for f in frames])


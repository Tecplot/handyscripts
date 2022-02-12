import tecplot

page = tecplot.active_page()
page.name = 'Page 001'

# prints: "Page 001"
print(page.name)

# prints: "Frame 001"
for frame in page.frames():
    print(frame.name)

import tecplot

# iterate over all frames in
# all pages and print their names
for page in tecplot.pages():
    for frame in page.frames():
        print(frame.name)

# store a persistent list of pages
pages = list(tecplot.pages())

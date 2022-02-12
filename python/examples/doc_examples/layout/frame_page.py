import tecplot

frame = tecplot.active_frame()
page = frame.page

# Will print: "Page 001"
print(page.name)

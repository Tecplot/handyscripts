import tecplot

page = tecplot.active_page()
frame1 = page.active_frame()
frame2 = page.add_frame()

assert not (frame1 == frame2)
assert page.active_frame() == frame2

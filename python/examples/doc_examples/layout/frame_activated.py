import tecplot

page = tecplot.active_page()
frame1 = page.active_frame()
frame2 = page.add_frame()

assert frame2.active

with frame1.activated():
    # frame1 is active only during this context
    assert frame1.active
    # there is only one frame active at a time
    assert not frame2.active

assert frame2.active

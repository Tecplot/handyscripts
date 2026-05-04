import tecplot

page1 = tecplot.active_page()
frame1 = page1.active_frame()
page2 = tecplot.add_page()
frame2 = page2.active_frame()
assert not (frame1.active and page1.active)
assert frame2.active and page2.active

frame1.activate()
assert not (frame2.active or page2.active)
assert frame1.active and page1.active

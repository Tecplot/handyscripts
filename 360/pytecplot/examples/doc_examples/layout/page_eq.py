import tecplot

page1 = tecplot.active_page()
page2 = tecplot.add_page()

assert page1 != page2
assert tecplot.active_page() == page2

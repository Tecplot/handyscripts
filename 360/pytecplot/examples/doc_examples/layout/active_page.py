import tecplot

#{DOC:highlight}[
page1 = tecplot.active_page()
#]
page2 = tecplot.add_page()

# page2 is now active
assert page2.active

# we can bring page1 back to the front:
page1.activate()
assert page1.active

import tecplot
page1 = tecplot.active_page()
#{DOC:highlight}[
page2 = tecplot.add_page()
#]
# page2 is now active
assert page2.active

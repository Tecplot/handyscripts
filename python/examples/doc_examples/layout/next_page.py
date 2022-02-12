import tecplot
from tecplot.layout import next_page

page1 = tecplot.active_page()
page2 = tecplot.add_page()
#{DOC:highlight}[
page3 = next_page()
#]

# page1 is now the active page
# and is the same as page3
assert page1.active
assert page3 == page1

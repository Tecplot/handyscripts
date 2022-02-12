import tecplot
page = tecplot.active_page()

frameA = page.add_frame()
frameA.name = 'A'

frameB = page.add_frame()
frameB.name = 'B'

assert frameB.active
#{DOC:highlight}[
assert frameA == page.frame('A')
#]
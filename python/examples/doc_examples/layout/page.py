import tecplot
page11 = tecplot.add_page()
page11.name = 'Page 11'
page12 = tecplot.add_page()
page12.name = 'Page 12'
#{DOC:highlight}[
assert page12 == tecplot.page('Page 1*')
#]

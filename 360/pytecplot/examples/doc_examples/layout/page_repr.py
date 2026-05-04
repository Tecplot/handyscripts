import tecplot
from tecplot.layout import Page

page = tecplot.active_page()

'''
The "repr" string of the Page is executable code.
The following will print: "Page(uid=1)"
'''
print(repr(page))

page2 = None
exec('page2 = '+repr(page))

'''
At this point, page2 is just another handle to
the exact same page object in the Tecplot Engine
'''
assert page2 == page

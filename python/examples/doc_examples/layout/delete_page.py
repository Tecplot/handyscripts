import tecplot as tp
from tecplot.exception import TecplotRuntimeError

page = tp.add_page()
#{DOC:highlight}[
tp.delete_page(page)
#]

next_page = tp.active_page()

assert page != next_page
assert not page.active

try:
    # the page is gone so activating
    # will produce an exception
    page.activate()
except TecplotRuntimeError as e:
    print(e)

del page # clear the python object

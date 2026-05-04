import tecplot as tp
page = tp.add_page()
assert page.exists
tp.delete_page(page)
assert not page.exists

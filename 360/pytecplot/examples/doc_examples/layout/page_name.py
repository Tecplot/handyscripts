import tecplot

page = tecplot.active_page()
page.name = 'My Data'

# prints: "this page: My Data"
print('this page:', page.name)

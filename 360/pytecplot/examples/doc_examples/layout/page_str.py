import tecplot
page = tecplot.active_page()
page.name = 'Page 001'

# will print: 'Page: "Page 001"'
print(page)

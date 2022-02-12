import tecplot as tp

aux = tp.active_page().aux_data
aux['Result'] = 3.14159

# prints: '3.14159' as a string
print(aux['Result'])

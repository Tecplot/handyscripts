import tecplot as tp

aux = tp.active_frame().aux_data
aux['info'] = 'Here is some information.'
aux['Xavg'] = 3.14159
aux['note'] = 'Aux data values are always converted to strings.'

'''
The following code will print:
    info: Here is some information.
    note: Aux data values are always converted to strings.
    Xavg: 3.14159
'''
for k, v in aux.items():
    print('{}: {}'.format(k,v))

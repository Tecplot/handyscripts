import tecplot as tp

aux = tp.layout.aux_data()
aux['info'] = '''\
This layout contains a lot of things:
    1. Something
    2. Something else
    3. Also this'''

'''
The following will print (including newlines):
    This layout contains a lot of things:
        1. Something
        2. Something else
        3. Also this
'''
print(aux['info'])

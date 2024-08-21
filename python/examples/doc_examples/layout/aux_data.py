import tecplot as tp


tp.session.connect()
aux = tp.layout.aux_data()
frame_aux_data = tp.active_frame().aux_data
frame_aux_data['gusto'] = 'l1', 'l2'
print(frame_aux_data)

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

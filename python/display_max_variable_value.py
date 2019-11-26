import numpy as np
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

#TODO: Make this work for 2D Cartesian. No Z.

def find_maximum(dataset, plot, zone, variable):
    #pull Tecplot 360 data set into Python Numpy
    arr = zone.values(variable)[:]

    #find node with variable max
    #use numpy.argmax() on the variable array to find the index of the maximum value
    node = np.argmax(arr)
    print('Node/Cell # of max value: '+ str(node))

    #Find XYZ position of node with max variable value
    x = zone.values(plot.axes.x_axis.variable)
    y = zone.values(plot.axes.y_axis.variable)
    try: z = zone.values(plot.axes.z_axis.variable)
    except: z = 0
    if zone.values(variable).location == ValueLocation.Nodal:
        print('Getting position of the node')
        x = x[node]
        y = y[node]
        try: z = z[node]
        except: z = 0
    else:
        print('Getting position of the cell center')
        nmap = zone.nodemap
        pts = nmap[node]
        x = np.average(x[:][pts])
        y = np.average(y[:][pts])
        try: z = np.average(z[:][pts])
        except: z = 0

    #max value in specified zone
    maxvar = zone.values(variable)[node]

    #max value for all zones
    #othermax = dataset.variable(varnum).max()
    print('Location: ({:.3g}, {:.3g}, {:.3g})'.format(x, y, z))
    print('Max value: {:.5g}'.format(maxvar))
    #print('Max value for all Zones: '+str(othermax))

    znname = 'MAXVARCALC 1D Zone'
    pointzone = dataset.zone(znname)
    if not pointzone:
        pointzone = dataset.add_ordered_zone(znname, 1)
        print("New Point Zone created.")
        
    pointzone.values(plot.axes.x_axis.variable)[0] = x
    pointzone.values(plot.axes.y_axis.variable)[0] = y
    try: pointzone.values(plot.axes.z_axis.variable)[0] = z
    except: None
    
    return pointzone, maxvar


def highlight_maximum(frame, plot, pointzone, variable, maxvar):

    #plot scatter for new point zone
    print("Turning off Scatter for all Zones.")
    # clever hack to use internal/undocumented pytecplot methods
    from tecplot.tecutil import sv
    oset = set(list(range(plot.num_fieldmaps)))
    tp.session.set_style(False, sv.FIELDMAP, sv.SCATTER, sv.SHOW,
                         uniqueid=frame.uid, objectset=oset)
        
    # this should be available in pytecplot 1.1
    #plot.fieldmaps().scatter.show = False
        
    # pure pytecplot API version (slow)
    #with tp.session.suspend():
    #    for item_index in range(0, dataset.num_zones):
    #        plot.fieldmap(item_index).scatter.show=False
     
    plot.show_scatter = True

    print("Applying Scatter for Point Zone.")
    fmap = plot.fieldmap(pointzone)
    fmap.show = True

    scatter = fmap.scatter
    scatter.show=True
    scatter.size=2
    scatter.color=Color.RedOrange
    scatter.symbol().shape=GeomShape.Diamond
    scatter.line_thickness=0.3

    #draw text box displaying max variable
    #TODO: Use python commands for text box, and overwrite any previous text boxes
    print("Adding text on plot for maximum value.")
    text = list(filter(lambda t: t.text_string.startswith('[MAXVARCALC] Maximum '), frame.texts()))
    msg = '[MAXVARCALC] Maximum {}: {:.3f}'.format(variable.name, maxvar)
    if text:
        text[-1].text_string = msg
    else:
        frame.add_text(msg, (3, 97), bold=False)

    #View Fit Surfaces
    try: plot.view.fit_surfaces(consider_blanking=True)
    except: None


if __name__ == '__main__':
    # Uncomment the following line to connect to a running instance of Tecplot 360:
    tp.session.connect()

    #NOTE: Run this script on a data set already loaded into Tecplot 360
    #plot
    frame = tp.active_frame()
    dataset = frame.dataset
    plot = frame.plot()

    #select zone and variable
    while True:
        zone_id = input('Zone (name or index): ')
        try:
            zone_id = int(zone_id) - 1
            if zone_id < 0:
                continue
        except: pass
        zone = dataset.zone(zone_id)
        if zone:
            break
        else:
            print('No zone found for', zone_id)

    while True:
        var_id = input('Variable (name or index): ')
        try:
            var_id = int(var_id) - 1
            if var_id < 0:
                continue
        except: pass
        variable = dataset.variable(var_id)
        if variable:
            break
        else:
            print('No variable found for', var_id)
        
    pointzone, maxvar = find_maximum(dataset, plot, zone, variable)
    highlight_maximum(frame, plot, pointzone, variable, maxvar)
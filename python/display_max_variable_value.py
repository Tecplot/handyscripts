import numpy as np
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

"""
    This script will find and display the maximum position on a specific 
    zone and variable. 
    
    To use: Load data into 360 and turn on PyTecplot Connections
        Enter Zone and Variable name or ID (one based) when prompted. 
        
    Returns: New one point zone with scatter turned on in Red. 
        Text box with maximum variable value identified. 

"""




def find_maximum(zone, variable):
    """
        Input: zone and variable
        Returns: x,y,z,value 

    """

    #pull Tecplot 360 data set into Python Numpy
    arr = zone.values(variable)[:]

    # Find list index with variable max
    # Use numpy.argmax() on the variable array to find the index of the maximum value
    max_idx = np.argmax(arr)
    print('Node/Cell # of max value: '+ str(max_idx))
    
    # Get max value in specified zone
    maxval = zone.values(variable)[max_idx]

    # Get handle to XYZ values arrays 
    plot = zone.dataset.frame.plot()
    x = zone.values(plot.axes.x_axis.variable)
    y = zone.values(plot.axes.y_axis.variable)
    try: z = zone.values(plot.axes.z_axis.variable)
    except: z = 0
    
    
    location = zone.values(variable).location 
    zonetype = zone.zone_type
    print(zonetype)
    if location == ValueLocation.Nodal :
    
        # Getting position of the node
        
        x_pos = x[max_idx]
        y_pos = y[max_idx]
        try: z_pos = z[max_idx]
        except: z_pos = 0
        
    elif (location == ValueLocation.CellCentered and 
        (zonetype == ZoneType.FEBrick or 
        zonetype == ZoneType.FEQuad or 
        zonetype == ZoneType.FETetra or
        zonetype == ZoneType.FETriangle)):
        
        # CellCentered Classic FE type
        
        # Getting position of the cell center
        nodes = zone.nodemap[max_idx]
        x_pos = np.average(x[:][nodes])
        y_pos = np.average(y[:][nodes])
        try: z_pos = np.average(z[:][nodes])
        except: z_pos = 0
        
    elif (location == ValueLocation.CellCentered and 
        (zonetype == ZoneType.FEPolygon or 
        zonetype == ZoneType.FEPolyhedron)):
        
        # CellCentered Polyhedral data

        fm = zone.facemap
        nodes = []
        # get the number of faces associated with the element
        num_faces = fm.num_faces(max_idx) 
        for f in range(num_faces):  
            num_nodes = fm.num_nodes(f, max_idx) # Get the number of nodes for each face
            for n in range(num_nodes): 
                node = fm.node(f,n,max_idx) # find all the nodes for all the faces
                if node not in nodes: # elimiate duplicates 
                    nodes.append(node)
        # Get the XYZ location of the the nodes of the element and calculate average
        x_pos = np.average(x[:][nodes])
        y_pos = np.average(y[:][nodes])
        try: z_pos = np.average(z[:][nodes])
        except: z_pos = 0
        
    else: 
        print("Unknown zone and cell type. Structured CellCentered data not supported") 

    print('Location: ({:.3g}, {:.3g}, {:.3g})'.format(x_pos, y_pos, z_pos))
    print('Max value: {:.5g}'.format(maxval))
    
    return x_pos, y_pos, z_pos, maxval
    
def create_scatter_point_zone(dataset, x_pos, y_pos, z_pos, znname='MAXVARCALC'):

    pointzone = dataset.add_ordered_zone(znname, 1)
    print("New Point Zone created.")
    axes = dataset.frame.plot().axes
    pointzone.values(axes.x_axis.variable)[0] = x_pos
    pointzone.values(axes.y_axis.variable)[0] = y_pos
    try: pointzone.values(axes.z_axis.variable)[0] = z_pos
    except: None
    
    return pointzone


def highlight_maximum(frame, pointzone, variable, maxvar):
    plot = frame.plot()
    #plot scatter for new point zone
    plot.fieldmaps().scatter.show = False   
    plot.show_scatter = True
    fmap = plot.fieldmap(pointzone)
    fmap.show = True

    scatter = fmap.scatter
    scatter.show=True
    scatter.size=2
    scatter.color=Color.RedOrange
    scatter.symbol().shape=GeomShape.Diamond
    scatter.line_thickness=0.3

    #draw text box displaying max variable
    print("Adding text on plot for maximum value.")
    text = list(filter(lambda t: t.text_string.startswith(pointzone.name), frame.texts()))
    msg = '{}: {:.3f}'.format(pointzone.name, maxvar)
    if text:
        text[-1].text_string = msg
    else:
        frame.add_text(msg, (3, 97), bold=False)

    #View Fit Surfaces
    try: plot.view.fit_surfaces(consider_blanking=True)
    except: None


if __name__ == '__main__':

    tp.session.connect()
    #NOTE: Run this script on a data set already loaded into Tecplot 360
    frame = tp.active_frame()
    dataset = frame.dataset
    plot = frame.plot()

    #select zone and variable
    while True:
        zone_id = input('Zone (name or 1 based index): ')
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
        var_id = input('Variable (name or 1 based index): ')
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
        
    x,y,z, maxvar = find_maximum(zone, variable)
    znname = "Maximum " + variable.name
    pointzone = create_scatter_point_zone(dataset, x,y,z, znname)
    highlight_maximum(frame, pointzone, variable, maxvar)
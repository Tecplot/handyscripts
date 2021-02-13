import argparse
import numpy as np
import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
import tputils


"""
    This script will find and display the maximum position on a specific 
    zone and variable. 
    
    Sample useage: 
    Finding the maximum in a zone (named myzone) for a variable (myvariable):
        display_max_variable_value.py -c -v my_var_name -z myzone

    Finding the maximum for each zone of a strand (zero indexed, i.e. 0 is the first strand):
        display_max_variable_value.py -c -v my_var_name -s 0

"""

def is_unstructured_zone(zone):
    return zone.zone_type in [ZoneType.FEBrick,ZoneType.FELineSeg,ZoneType.FEQuad,ZoneType.FETetra,ZoneType.FETriangle]
        
def is_polytope_zone(zone):
    return zone.zone_type in [ZoneType.FEPolygon,ZoneType.FEPolyhedron]


def find_maximum(zone, variable):
    """
        Input: zone and variable
        Returns: x,y,z,value 

    """

    #pull Tecplot 360 data set into Python Numpy
    arr = zone.values(variable)[:]

    # Find list index with variable max
    # Use numpy.argmax() on the variable array to find the node/cell index of the maximum value
    max_idx = np.argmax(arr)
    # print('Node/Cell # of max value: '+ str(max_idx))
    
    # Get max value in specified zone
    maxval = zone.values(variable)[max_idx]

    # Get handle to XYZ values arrays 
    plot = zone.dataset.frame.plot()
    x = zone.values(plot.axes.x_axis.variable)
    y = zone.values(plot.axes.y_axis.variable)
    try: z = zone.values(plot.axes.z_axis.variable)
    except: z = 0
    
    
    location = zone.values(variable).location 
    
    if location == ValueLocation.Nodal :
    
        # Getting position of the node
        
        x_pos = x[max_idx]
        y_pos = y[max_idx]
        try: z_pos = z[max_idx]
        except: z_pos = 0
        
    elif location == ValueLocation.CellCentered:
        element = max_idx
        if is_unstructured_zone(zone):
            nodes = zone.nodemap[element]        
        elif is_polytope_zone(zone):
            fm = zone.facemap 
            nodes = []
            # get the number of faces associated with the element
            num_faces = fm.num_faces(element) 
            for f in range(num_faces):  
                num_nodes = fm.num_nodes(f, element) # Get the number of nodes for each face
                for n in range(num_nodes): 
                    node = fm.node(f,n,element) # find all the nodes for all the faces
                    if node not in nodes: # elimiate duplicates 
                        nodes.append(node)
        else: 
            print('Structured data not supported') 
            exit()

        # Get the XYZ location of the the nodes of the element and calculate average
        x_pos = np.average(x[:][nodes])
        y_pos = np.average(y[:][nodes])
        try: z_pos = np.average(z[:][nodes])
        except: z_pos = 0
        
    else: 
        print("Unknown zone and cell type. Structured CellCentered data not supported") 

    #print('Location: ({:.3g}, {:.3g}, {:.3g})'.format(x_pos, y_pos, z_pos))
    #print('Max value: {:.5g}'.format(maxval))
    
    return x_pos, y_pos, z_pos, maxval
    
def create_scatter_point_zone(dataset, x_pos, y_pos, z_pos, 
            znname='MAXVARCALC', sol_time=0, strand=0):

    pointzone = dataset.add_ordered_zone(znname, 1,
        solution_time=sol_time, 
        strand_id=strand)
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
    #View Fit Surfaces
    try: plot.view.fit_surfaces(consider_blanking=True)
    except: None

def draw_text_single_timestep(frame,pointzone, variable, maxvar):
    #draw text box displaying max variable
    print("Adding text on plot for maximum value.")
    text = list(filter(lambda t: t.text_string.startswith(pointzone.name), frame.texts()))
    msg = '{}: {:.3f}'.format(pointzone.name, maxvar)
    if text:
        text[-1].text_string = msg
    else:
        frame.add_text(msg, (3, 97), bold=False)


def draw_text_multiple_timestep(frame, aux_str, variable):
    #draw text box displaying max variable from aux data 
    active_offset = len(list(plot.active_fieldmaps)) #get last active fieldmaps
    msg = "{} maximum: &(AUXZONE[ACTIVEOFFSET={}]:{})".format(variable.name, active_offset, aux_str) 
    
    text = list(filter(lambda t: t.text_string.startswith(variable.name), frame.texts()))
    if text:
        text[-1].text_string = msg
    else:
        frame.add_text(msg, (3, 97), bold=False)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='Connected mode')
    parser.add_argument('-v', '--var', required=True, help='Zone name or 0 based index')
    parser.add_argument('-z', '--zone', help='Zone name or 0 based index')
    parser.add_argument('-s', '--strand', type=int, help='Strand ID for transient zones')
    args = parser.parse_args()

    if args.c:
        tp.session.connect()
    
    frame = tp.active_frame()
    dataset = frame.dataset
    plot = frame.plot()
    
    
    try: 
        try: var = int(args.var)
        except: var = args.var
            
        variable = dataset.variable(var)
        print(variable)
    except: 
        print('unrecognized variable')
        exit()
        
    if args.zone: 
        try:
            zone = dataset.zone(int(args.zone))
        except ValueError:
            zone = dataset.zone(args.zone)
        x,y,z, maxvar = find_maximum(zone, variable)
        znname = "Maximum " + variable.name
        pointzone = create_scatter_point_zone(dataset, x,y,z, znname)
        highlight_maximum(frame, pointzone, variable, maxvar)
        draw_text_single_timestep(frame, pointzone, variable, maxvar)
        
        
    elif args.strand: 
        # loop through zones 
        # Get zones associated with the strand 
        zones_by_strands = tputils.get_zones_by_strand(dataset)
        zns = zones_by_strands[args.strand]
        aux_str = 'max_{}'.format(variable.name) # Create aux data string name
        strand = tputils.max_strand(dataset) +1 # Strand number for the new point zones 
        for zn in zns: 
            x,y,z, maxvar = find_maximum(zn, variable)
            print (zn.name, x,y,z, maxvar)
            znname = "Maximum {} - t = {}".format(variable.name, zn.solution_time)
            pointzone = create_scatter_point_zone(dataset, x,y,z, znname, zn.solution_time, strand)
            pointzone.aux_data[aux_str] = str(maxvar)
        highlight_maximum(frame, pointzone, variable, maxvar)
        draw_text_multiple_timestep(frame,aux_str,variable) 
        
        
            
    else: 
        print('Unrecognized zone') 
        exit()
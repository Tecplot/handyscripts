import logging
import tecplot as tp
from tecplot.constant import *

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

def get_surface_data_ascii(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        
        first_line = lines[0].split()
        node_count = int(first_line[0])
        cell_count = int(first_line[2])
        
        nodes = []
        start = 1
        end = node_count+1
        for line in lines[start:end]:
            index,x,y,z = list(map(float, line.split()))
            nodes.extend([x,y,z])

        verts = []
        start = end
        end = start+cell_count
        for line in lines[start:end]:
            v1,v2,v3,ignore = list(map(int, line.split()))
            verts.extend([v1,v2,v3])

        assert(node_count == len(nodes)/3)
        assert(cell_count == len(verts)/3)
        return nodes, verts

def load_surface_file(file_name):
    """Load a CONVERGE surface data file into Tecplot 360.
    This will create a new dataset in the active frame or create a new frame
    if the active frame already has a dataset.
    """
    import os
    
    try:
        print("Loading ASCII file")
        nodes, verts = get_surface_data_ascii(file_name)
        node_count = int(len(nodes)/3)
        cell_count = int(len(verts)/3)
        
        with tp.session.suspend():
            frame = tp.active_frame()
            if frame.has_dataset:
                frame = tp.active_page().add_frame()
            ds = tp.active_frame().dataset
            ds.add_variable("X")
            ds.add_variable("Y")
            ds.add_variable("Z")
            #ds.add_variable("BoundaryID")
            value_locations = [ValueLocation.Nodal, ValueLocation.Nodal, ValueLocation.Nodal, ValueLocation.CellCentered]
            zone = ds.add_fe_zone(ZoneType.FETriangle, os.path.basename(file_name), node_count, cell_count, locations=value_locations)

            xvals = nodes[0:node_count*3:3]
            yvals = nodes[1:node_count*3:3]
            zvals = nodes[2:node_count*3:3]

            zone.values('X')[:] = xvals
            zone.values('Y')[:] = yvals
            zone.values('Z')[:] = zvals
            #zone.values('BoundaryID')[:] = components

            zero_based_verts = [v-1 for v in verts]
            zone.nodemap.array[:] = zero_based_verts

            tp.active_frame().plot_type = PlotType.Cartesian3D
            tp.active_frame().plot().fieldmap(zone).effects.lighting_effect=LightingEffect.Paneled
    except:
        print("ASCII failed")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Load or convert CONVERGE surface.dat files")
    parser.add_argument("infile", help="CONVERGE surface.dat file to load")
    parser.add_argument("-outfile", help="Specify an output file if you want to convert to PLT file", default=None)
    args = parser.parse_args()
    
    if not args.outfile:
        tp.session.connect()
        
    log.info('reading in file: {}'.format(args.infile))
    load_surface_file(args.infile)
    tp.active_frame().plot_type = PlotType.Cartesian3D

    if args.outfile:
        log.info('writing to file: {}'.format(args.outfile))
        tp.data.save_tecplot_plt(args.outfile)


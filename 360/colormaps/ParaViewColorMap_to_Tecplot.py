import json
import xml.dom.minidom
import sys
import glob
import os
import math

def consolodate_close_control_points(control_points):
    #
    # If two control points are sufficently close, use LEAD/TRAIL
    #
    FRAC = 0
    LEAD = 1
    TRAIL = 2
    final_control_points = [control_points[0]]
    for i in range(1, len(control_points)):
        previous_control_point = control_points[i-1]
        control_point = control_points[i]
        frac = control_point[FRAC]
        prev_frac = previous_control_point[FRAC]
        if math.isclose(frac,prev_frac,abs_tol=0.0001):

            previous_control_point = (prev_frac, control_point[TRAIL], previous_control_point[TRAIL])
            final_control_points[-1] = previous_control_point
        else:
            final_control_points.append(control_point)

    return final_control_points

def create_colormap_control_points_from_paraview_json_file(colormap_file):
    #
    # This function handles multiple colormaps within a JSON file and will return
    # a list of colormaps, represented as 2-value tuples. Where name is the first value
    # in the tuple and the set of control points is the second value
    #
    with open(colormap_file, "r") as f:
        j = json.load(f)

    colormaps = []
    for i in j:
        name = "paraview - {}".format(i['Name'])
        rgb_points = i['RGBPoints'] 
        num_rgb_points = int(len(rgb_points)/4)
        
        num_control_points = min(50, num_rgb_points)
        min_frac = rgb_points[0]
        max_frac = rgb_points[-4]
        control_points = []
        for control_point in range(num_control_points):
            rgb_point = int((control_point/num_control_points)*num_rgb_points)
            raw_frac = rgb_points[rgb_point*4]
            frac = (raw_frac - min_frac) / (max_frac - min_frac)
            r = rgb_points[rgb_point*4 + 1] * 255
            g = rgb_points[rgb_point*4 + 2] * 255
            b = rgb_points[rgb_point*4 + 3] * 255
            control_points.append((frac, (r,g,b), (r,g,b)))

        final_control_points = consolodate_close_control_points(control_points)

        colormaps.append((name, final_control_points))

    return colormaps

def get_rgb(control_point):
    max_rgb = 255
    r = int(float(control_point.getAttribute("r")) * max_rgb)
    g = int(float(control_point.getAttribute("g")) * max_rgb)
    b = int(float(control_point.getAttribute("b")) * max_rgb)
    return (r,g,b)
  
def create_colormap_control_points_from_paraview_xml_file(colormap_file):
    dom = xml.dom.minidom.parse(colormap_file)
    name = dom.getElementsByTagName("ColorMap")[0].getAttribute("name")
    rgb_points = dom.getElementsByTagName("Point")
    num_rgb_points = len(rgb_points)
    num_control_points = min(50, num_rgb_points)

    min_frac = float(rgb_points[0].getAttribute("x"))
    max_frac = float(rgb_points[-1].getAttribute("x"))
    control_points = []
    for index in range(num_control_points):
        rgb_point_index = int((index/num_control_points)*num_rgb_points)
        control_point = rgb_points[rgb_point_index]
        raw_frac = float(control_point.getAttribute("x"))
        frac = (raw_frac - min_frac) / (max_frac - min_frac)
        
        lead = get_rgb(control_point)
        trail = lead

        control_points.append((frac, lead, trail))

    final_control_points = consolodate_close_control_points(control_points)
    return 'paraview - {}'.format(name), final_control_points
            

def create_tecplot_colormap_command_from_control_points(name, control_points):
    num_rgb_points = len(control_points)
    num_control_points = min(50, num_rgb_points)

    indexes = []
    cmd = ""
    for index in range(num_control_points):
        rgb_point_index = int((index/num_control_points)*num_rgb_points)
        control_point = control_points[rgb_point_index]
        frac = control_point[0]
        lead = control_point[1]
        trail = control_point[2]

        #
        # Avoid duplicate indices
        #
        if rgb_point_index in indexes:
            continue
        indexes.append(rgb_point_index)
            
        lead_r = lead[0]
        lead_g = lead[1]
        lead_b = lead[2]
        trail_r = trail[0]
        trail_g = trail[1]
        trail_b = trail[2]
        control_point_number = len(indexes)
        cmd += "  CONTROLPOINT %d {COLORMAPFRACTION = %f LEADRGB {R=%d G=%d B=%d} TRAILRGB {R=%d G=%d B=%d}}\n" %(control_point_number,frac,lead_r,lead_g,lead_b,trail_r,trail_g,trail_b)

    final_cmd = "$!CREATECOLORMAP\n"
    final_cmd += "  NAME = '{}'\n".format(name)
    final_cmd += "  NUMCONTROLPOINTS = {}\n".format(len(indexes))
    final_cmd += cmd
    return final_cmd
        

colormap_files = glob.glob(sys.argv[1])
outdir = sys.argv[2]
for colormap_file in colormap_files:
    if colormap_file.endswith(".json"):
        colormaps = create_colormap_control_points_from_paraview_json_file(colormap_file)
        outfile = os.path.join(outdir, "{}.map".format(os.path.basename(colormap_file)))
        print("Writing to: ", outfile)
        with open(outfile, "w") as f:
            f.write("#!MC 1410\n")
            for cmap in colormaps:
                name = cmap[0]
                control_points = cmap[1]
                cmd = create_tecplot_colormap_command_from_control_points(name, control_points)
                f.write(cmd)
    elif colormap_file.endswith(".xml"):
        name, control_points = create_colormap_control_points_from_paraview_xml_file(colormap_file)
        cmd = create_tecplot_colormap_command_from_control_points(name, control_points)
        outfile = os.path.join(outdir, "{}.map".format(os.path.basename(colormap_file)))
        print("Writing to: ", outfile)
        with open(outfile, "w") as f:
            f.write("#!MC 1410\n")
            f.write(cmd)


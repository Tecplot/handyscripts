#import cmocean
import matplotlib.pyplot as plt
import numpy as np
import tecplot as tp
from tecplot.constant import *

colormaps = [
    plt.get_cmap('viridis')
    ,plt.get_cmap('turbo')
    ,plt.get_cmap('plasma')
    ,plt.get_cmap('inferno')
    ,plt.get_cmap('magma')
    #,cmocean.cm.thermal
    #,cmocean.cm.haline
    #,cmocean.cm.solar
    #,cmocean.cm.ice
    #,cmocean.cm.gray
    #,cmocean.cm.oxy
    #,cmocean.cm.deep
    #,cmocean.cm.dense
    #,cmocean.cm.algae
    #,cmocean.cm.matter
    #,cmocean.cm.turbid
    #,cmocean.cm.speed
    #,cmocean.cm.amp
    #,cmocean.cm.tempo
    #,cmocean.cm.phase
    #,cmocean.cm.balance
    #,cmocean.cm.delta
    #,cmocean.cm.curl
]

def create_tecplot_colormap_command(cm, fractions, suffix=""):
    #print("NumPoints ", cm.N)
    cmd = "$!CREATECOLORMAP\n"
    colormapname = "{}{}".format(cm.name,suffix)
    cmd += "  NAME = '{}'\n".format(colormapname)
    cmd += "  NUMCONTROLPOINTS = {}\n".format(len(fractions))
    fractions = list(fractions)
    fractions.sort()
    for i,frac in enumerate(fractions):
        point = i+1
        value = int(frac*cm.N)
        #print("Point: ", point)
        #print("Value: ", value)
        
        # Handle sharp changes in the colormap
        lead = cm(value)
        trail = cm(value-1)
        if np.allclose(trail, lead, 0.2):
            trail = lead
            
        max_rgb = 255
        lead_r = lead[0]*max_rgb
        lead_g = lead[1]*max_rgb
        lead_b = lead[2]*max_rgb
        trail_r = trail[0]*max_rgb
        trail_g = trail[1]*max_rgb
        trail_b = trail[2]*max_rgb
        cmd += "  CONTROLPOINT %d {COLORMAPFRACTION = %f LEADRGB {R=%d G=%d B=%d} TRAILRGB {R=%d G=%d B=%d}}\n" %(point,frac,lead_r,lead_g,lead_b,trail_r,trail_g,trail_b)
    return colormapname, cmd

with open("colormaps.map", "w") as cmap_file:
    cmap_file.write("#!MC 1410\n")
    for cmap in colormaps:
        # 11 control points is a pretty good approximation. In some cases you may need more or may need
        # very specific control point fractions (like for the cmocean.cm.oxy colormap)
        num_control_points = 11
        fractions = set(np.linspace(0.0,1.0,num_control_points))
        ret = create_tecplot_colormap_command(cmap, fractions, suffix=" - matplotlib")
        print(ret[0])
        cmap_file.write(ret[1])
print("Wrote colormaps to: colormaps.map")




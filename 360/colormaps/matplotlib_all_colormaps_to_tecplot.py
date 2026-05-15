import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path

def create_tecplot_colormap_command(cm, fractions, suffix=""):
    cmd = "$!CREATECOLORMAP\n"
    colormapname = "{}{}".format(cm.name,suffix)
    cmd += "  NAME = 'matplotlib - {}'\n".format(colormapname)
    cmd += "  NUMCONTROLPOINTS = {}\n".format(len(fractions))
    fractions = list(fractions)
    fractions.sort()
    for i,frac in enumerate(fractions):
        point = i+1
        value = int(frac*cm.N)
        
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

def get_all_colormaps():
    colormap_names = sorted(plt.colormaps())
    return [plt.get_cmap(name) for name in colormap_names]


def default_output_path():
    return Path(__file__).with_name("_matplotlib_all_colormaps.map")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Write all registered Matplotlib colormaps to one Tecplot .map file."
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=default_output_path(),
        help="Output .map file path. Defaults to _matplotlib_all_colormaps.map next to this script.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    colormaps = get_all_colormaps()

    num_control_points = 11
    fractions = set(np.linspace(0.0,1.0,num_control_points))

    with args.output.open("w", encoding="utf-8", newline="\n") as outfile:
        outfile.write("#!MC 1410\n")
        for colormap in colormaps:
            name, cmd = create_tecplot_colormap_command(colormap, fractions)
            print(name)
            outfile.write(cmd)

    print("Wrote {}".format(args.output))


if __name__ == "__main__":
    main()

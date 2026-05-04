import json
import re
import tecplot as tp
from tecplot.constant import Color

def get_rgb(item):
    delimiters = "rgb", "(", ",", ")", "\n"
    pattern = '|'.join(map(re.escape, delimiters))
    rgb = [int(i) for i in re.split(pattern, item) if i.isdigit()]
    assert(len(rgb) == 3)
    return rgb

def get_rgb_values(palette, num_colors):
    # Source: https://colorbrewer2.org/export/colorbrewer.json
    with open('colorbrewer2.json') as f:
        data = json.load(f)
        if not palette in data:
            print("Bad Selection")
        else:
            colors = data[palette]
            color_counts = [int(i) for i in colors if i.isdigit()]
            #print(color_counts)
            
            min_colors = min(color_counts)
            max_colors = max(color_counts)
            color_index = num_colors
            if num_colors < min_colors:
                color_index = min_colors
            if num_colors > max_colors:
                color_index = max_colors
            
            result = []
            for str_rgb in colors[str(color_index)]:
                res = get_rgb(str_rgb)
                result.append(res)
            if num_colors <= len(result):
                return result[:num_colors]
            else:
                assert(num_colors > len(result))
                new_result = []
                index = 0
                for i in range(num_colors):
                    new_result.append(result[index])
                    index = index+1
                    if index > len(result)-1:
                        index = 0
                return new_result
    return []

def get_color_palettes():
    palettes = []
    with open('colorbrewer2.json') as f:
        data = json.load(f)
        for k in data:
            palettes.append(k)
    return palettes

def setup_colors(linemaps, palette):
    MAX_CUSTOM_COLOR = 56
    linemaps = list(linemaps)
    rgb_values = get_rgb_values(palette, len(linemaps))
    macro_command = ""
    for i,rgb in enumerate(rgb_values):
        r,g,b = rgb[0], rgb[1], rgb[2]
        custom_index = MAX_CUSTOM_COLOR-i
        if i >= MAX_CUSTOM_COLOR:
            break
        macro_command += "$!BASICCOLOR CUSTOM%d {R=%d G=%d B=%d}\n"%(custom_index, r,g,b)
    #print(macro_command)
    tp.macro.execute_command(macro_command)
    for i,lmap in enumerate(tp.active_frame().plot().linemaps()):
        if i >= MAX_CUSTOM_COLOR:
            break
        lmap.line.color = Color.Custom56.value-i
        #print(lmap.zone_index, lmap.line.color)


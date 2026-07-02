import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")
ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)
left_func = ds.scalar_functions[0]
mid_y = 0.5 * (ds.ymin + ds.ymax)
mid_z = 0.5 * (ds.zmin + ds.zmax)
start = (ds.xmin + 0.2 * (ds.xmax - ds.xmin), mid_y, mid_z)
end = (ds.xmin + 0.4 * (ds.xmax - ds.xmin), mid_y, mid_z)

plot = fv.vis.create_plot2d(
    left_axis_func=left_func,
    show_plot=True,
    show_path=True,
)

path = plot.create_line_path_volume(
    start,
    end,
)

plot.left_axis.label = left_func
plot.horizontal_axis.label = "Distance"
output_txt = os.path.join(os.path.expanduser("~"), "line_path.txt")
path.export_txt(output_txt)
print(f"Saved path data: {output_txt}")

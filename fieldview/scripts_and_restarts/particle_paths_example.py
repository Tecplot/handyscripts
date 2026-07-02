import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

ppath_file = os.path.join(os.path.dirname(__file__), "particle_paths_example.fvp")

ppath = fv.vis.create_particle_paths(
    ds,
    filename=ppath_file,
    coloring=fv.constant.Coloring.SCALAR,
    scalar_func="Duration",
    display_type=fv.constant.PathsDisplayType.SPHERES_AND_LINES,
    animate=True,
    animate_direction=fv.constant.AnimationDirection.FORWARD,
    animate_divs=25,
)

ppath.select_by_initial_value = True
ppath.select_by_initial_value_variable = "Duration"

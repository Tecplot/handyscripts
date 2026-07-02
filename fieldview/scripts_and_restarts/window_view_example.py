import os

import fieldview as fv


data_dir = os.path.join(fv.home, "examples", "f18")

ds = fv.data.load_plot3d(
    os.path.join(data_dir, "f18i9b_g_bin"),
    os.path.join(data_dir, "f18i9b_q_bin"),
)

split = fv.layout.split_horizontal(mode="copy", window=1)

# Keep windows independent; otherwise view changes in one pane can affect both.
fv.layout.set_view_sync(False, window=1)
fv.layout.set_view_sync(False, window=split.new_window)

fv.view.reset(window=1)
fv.view.set_perspective(False, window=1)
fv.view.align("+y", window=1)

fv.view.reset(window=split.new_window)
fv.view.set_perspective(False, window=split.new_window)
fv.view.align("+x", window=split.new_window)

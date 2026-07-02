import fieldview as fv


# get_session_state(): one-shot session snapshot (data loaded flag, bounds,
# function lists, and grouped object info) useful for startup checks.
state = fv.data.get_session_state()
if not state.data_loaded:
    raise RuntimeError("No dataset is loaded. Run the prep script first.")

# get_all_objects(): returns live typed wrappers you can modify directly
# (Boundary/Coord/Comp/Iso/Paths/etc.) in the current session.
objects = fv.get_all_objects()
if not objects.boundary_list:
    raise RuntimeError("No boundary surface found. Run the prep script first.")

bnd = objects.boundary_list[0]

# Requested edits on the existing boundary/view.
fv.view.set_outline(False)  # turn off outline/grid view
bnd.coloring = fv.constant.Coloring.SCALAR
bnd.display_type = fv.constant.DisplayType.SMOOTH
bnd.scalar_minmax.show = True
bnd.show_mesh = True

fv.view.reset()
fv.camera.zoom(3.0)
fv.camera.pan(0.06, 0.0)

print("Reused boundary object and updated display settings.")

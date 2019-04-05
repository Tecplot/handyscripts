import tecplot as tp
from tecplot.constant import ValueLocation

def probe_index_through_time(zone, variable, index_number):
    """
    Follows a specific index in a zone/variable through time and returns a list of tuples.
    The length of the list is equivalent to the number of zones in the strand associated with
    the input zone. Each tuple is (solution_time, element_value)

    zone - Any Zone in the strand you want to interrogate. All zones must have the same number of points/elements
    variable - The Variable you want to interrogate. All Zone/Vars must have the same value location (cell-centered/node-centered)
    index_number - 0-based node/element number you want to follow through time.  For cell-centered variables this should
        be an element number. For node-centered variables this should be a node number.

    Example:
      import tecplot as tp
      import tpplot
      import tpprobe
      
      tp.session.connect()
      ds = tp.active_frame().dataset
      zone = ds.zone(0)
      var = ds.variable("salinity")
      element_num = 128
      result = tpprobe.probe_element_through_time(zone, var, element_num)
      tpplot.plot_line_data(result, "Time vs {}".format(var.name), "Time", var.name)
    """

    result = []
    zones = [z for z in tp.active_frame().dataset.zones() if z.strand == zone.strand]
        
    vals = zone.values(variable)
    num_vals = len(vals)
    var_location = vals.location

    for z in zones:
        vals = z.values(variable.name)

        if len(vals) != num_vals:
            raise Exception("All zones must have the same number of points.")
        if vals.location != var_location:
            raise Exception("The variable must have the same value location (cell-centered or nodal).")

        result.append((z.solution_time, vals[index_number]))
    return result

def probe_element_through_time(zone, variable, element_number):
    """
    Follows a specific element in a zone/variable through time and returns a list of tuples.
    The length of the list is equivalent to the number of zones in the strand associated with
    the input zone. Each tuple is (solution_time, element_value)

    zone - Any Zone in the strand you want to interrogate. All zones must have the same number of elements
    variable - The Variable you want to interrogate. Variable values must be cell-centered
    element_number - 0-based element number you want to follow through time
    """

    vals = zone.values(variable)
    if vals.location != ValueLocation.CellCentered:
        raise Exception("Probe element through time requires a cell-centered variable.")

    return probe_index_through_time(zone, variable, element_number)

def probe_node_through_time(zone, variable, node_number):
    """
    Follows a specific node in a zone/variable through time and returns a list of tuples.
    The length of the list is equivalent to the number of zones in the strand associated with
    the input zone. Each tuple is (solution_time, element_value)

    zone - Any Zone in the strand you want to interrogate. All zones must have the same number of points
    variable - The Variable you want to interrogate. Variable values must be node-centered
    node_number - 0-based node number you want to follow through time
    """

    vals = zone.values(variable)
    if vals.location != ValueLocation.Nodal:
        raise Exception("Probe node through time requires a node-centered variable.")

    return probe_index_through_time(zone, variable, node_number)


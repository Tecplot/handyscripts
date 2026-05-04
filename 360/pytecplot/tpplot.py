import tecplot as tp
from tecplot.constant import ValueLocation, PlotType


def add_variable_to_dataset(dataset, var_name):
    """
    Convenience function to add a variable to the dataset
    only if the variable doesn't already exist. This function
    is case sensitive.  "radius" and "Radius" are two different 
    variable names.
    returns the Variable object associated with the variable name
    """
   
    if var_name not in dataset.variable_names:
        return dataset.add_variable(var_name)
    return dataset.variable(var_name)

def add_line_zone(data, zone_name, x_var_name, y_var_name):
    """
    Adds data to the existing dataset. The data is expected
    to be a list of 2-valued tuples:
    data = [
     (x1, y1),
     (x2, y2),
     ...
     (xn, yn)
     ] 
    returns a newly created zone
    """
    ds = tp.active_frame().dataset
    add_variable_to_dataset(ds, x_var_name)
    add_variable_to_dataset(ds, y_var_name)
    zone = ds.add_ordered_zone(zone_name, (len(data),1,1), locations=[ValueLocation.Nodal]*ds.num_variables)
    zone.values(x_var_name)[:] = [n[0] for n in data]
    zone.values(y_var_name)[:] = [n[1] for n in data]
    return zone
    

def plot_line_data(data, zone_name, x_var_name, y_var_name):
    """
    Creates a new frame and plots the data. The data is expected
    to be a list of 2-valued tuples:
    data = [
     (x1, y1),
     (x2, y2),
     ...
     (xn, yn)
     ]
   
    """
    zone = add_line_zone(data, zone_name,  x_var_name, y_var_name)
    ds = zone.dataset
       
    line_plot_frame = tp.active_page().add_frame() 
    line_plot_frame.plot_type = PlotType.XYLine
    plot = line_plot_frame.plot()
    plot.delete_linemaps()
    # &ZN& is a key word which will use the zone's name as the name of the line map
    plot.add_linemap("&ZN&", zone=zone, x=ds.variable(x_var_name),y=ds.variable(y_var_name))
    plot.view.fit()
    return zone



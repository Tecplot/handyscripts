"""Plots the maximums for one zone through time

Description
-----------
This connected-mode script creates a line graph of the min/max values from a zone
over time.

Usage:
    > python plot_min_max_over_time.py

For example data, use the ICE example from the Getting Started Bundle
https://tecplot.azureedge.net/data/360GettingStarted.zip
"""

import tecplot as tp
from tecplot.constant import *
tp.session.connect() #connect to a live running instance of Tecplot 360

zone_name = input("Enter the zone name to investigate (use '*' for all zones, wildcards accepted to match multiple zones):") 
var_name  = input("Enter the variable name to investigate (e.g 'Pressure'):")

# Suspend the interface to speed up execution time
with tp.session.suspend():
    dataset = tp.active_frame().dataset
    min_values = []
    max_values = []
    var = dataset.variable(var_name)
    zones_to_check = list(dataset.zones(zone_name))
    for z in dataset.zones(zone_name):
        print("Getting min/max for zone:",z.name)
        min_values.append((z.solution_time, z.values(var).min()))
        max_values.append((z.solution_time, z.values(var).max()))

    # Create a new frame and stuff the extracted values into it for plotting
    new_frame = tp.active_page().add_frame()
    time_var_name = 't'
    ds = new_frame.create_dataset(f'Min/Max {var.name} over time', [time_var_name,var.name])

    zone = ds.add_ordered_zone(f'Min {var.name} over time ({zone_name})', len(min_values))
    zone.values(time_var_name)[:] = [v[0] for v in min_values]
    zone.values(var.name)[:]      = [v[1] for v in min_values]
    zone.aux_data['Source_Zone'] = zone_name
    zone.aux_data['Source_Var'] = var_name

    zone = ds.add_ordered_zone(f'Max {var.name} over time ({zone_name})', len(max_values))
    zone.values(time_var_name)[:] = [v[0] for v in max_values]
    zone.values(var.name)[:]      = [v[1] for v in max_values]
    zone.aux_data['Source_Zone'] = zone_name
    zone.aux_data['Source_Var'] = var_name

    line_plot = new_frame.plot(PlotType.XYLine)
    line_plot.activate()
    line_plot.linemaps().show = True
    line_plot.view.fit()
    
    

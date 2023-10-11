import time
import tecplot as tp
from tecplot.constant import *

def compute_radius_and_theta(axial_direction="X", center_point=(0,0,0)):
    center_x, center_y, center_z = center_point

    var_names = list(tp.active_frame().dataset.variable_names)
    if "Radius" in var_names and "Theta" in var_names:
        print("Radius and Theta already exist. Skipping calculation")
        return

    print("Computing Radius and Theta")

    if axial_direction == "X":
        tp.data.operate.execute_equation(equation=f'{{Radius}} = sqrt((Y-{center_y})**2 + (Z-{center_z})**2)', ignore_divide_by_zero=True)
        tp.data.operate.execute_equation(equation=f'{{Theta}} = atan2((Y-{center_y}),(Z-{center_z}))', ignore_divide_by_zero=True)
    elif axial_direction == "Y":
        tp.data.operate.execute_equation(equation=f'{{Radius}} = sqrt((X-{center_x})**2 + (Z-{center_z})**2)', ignore_divide_by_zero=True)
        tp.data.operate.execute_equation(equation=f'{{Theta}} = atan2((X-{center_x}),(Z-{center_z}))', ignore_divide_by_zero=True)
    elif axial_direction == "Z":
        tp.data.operate.execute_equation(equation=f'{{Radius}} = sqrt((X-{center_x})**2 + (Y-{center_y})**2)', ignore_divide_by_zero=True)
        tp.data.operate.execute_equation(equation=f'{{Theta}} = atan2((X-{center_x}),(Y-{center_y}))', ignore_divide_by_zero=True)


def create_annular_slice(axial_direction="X", radius=0.0, center_point=(0,0,0)):
    ds = tp.active_frame().dataset
    
    compute_radius_and_theta(axial_direction, center_point)

    """
    Iso-surface method
    ------------------
    This method extracts an iso-surface at a constant radius. This method benefits from
    having the resulting grid be a good representation of the source grid. The problem with
    this method is that the resulting iso-surface will have a strip of cells that span the
    360-0 degree boundary. In 2D plots, these cells will be stretched across the entire plot. To
    combat this we use value blanking at the minimum of one of the axis variables (which corresponds
    with the periodic Theta boundary).  You do lose a small amount of information at the edges of the 
    plot, and may need to hand adjust this value a little.
    """
    
    # Extract and Iso-Surface at the specified Radius
    print(f"Extracting iso-surface at radius={radius}")
    threed_plot = tp.active_frame().plot(PlotType.Cartesian3D)
    threed_plot.contour(0).variable = ds.variable("Radius")
    threed_plot.isosurface(0).isosurface_values[0] = radius
    threed_plot.show_isosurfaces = True

    num_zones = ds.num_zones
    tp.macro.execute_extended_command(command_processor_id='Extract Over Time',
        command='ExtractIsoSurfaceOverTime')

    # Grab the first extracted iso-surface
    iso_zone = ds.zone(num_zones)
    
    print("Creating 2D Plot")
    #
    # Create the 2D plot of the unwrapped annular slice, by plotting just the "left" and "right"
    # sides that we just extracted
    #
    twod_frame = tp.active_page().add_frame()
    twod_frame.plot_type=PlotType.Cartesian2D
    plot = twod_frame.plot()
    plot.activate()
    plot.solution_time = iso_zone.solution_time
    axes = plot.axes
    axes.x_axis.variable = ds.variable("Theta")
    
    # Assuming that X,Y,Z are the first three variables
    axis_num_map = {"X":0, "Y":1, "Z":2}
    axes.y_axis.variable = ds.variable(axis_num_map[axial_direction])
    axes.axis_mode=AxisMode.Independent
    plot.show_contour = True
    plot.fieldmaps().show = False
    plot.fieldmap(iso_zone).show = True
    plot.view.fit()

    if axial_direction == "Z":
        var_num_to_blank = axis_num_map["Y"]
    else:
        var_num_to_blank = axis_num_map["Z"]

    blanking = plot.value_blanking
    blanking.active=True
    blanking.constraint(0).active=True
    blanking.constraint(0).variable_index=var_num_to_blank
    blanking.constraint(0).comparison_operator=RelOp.LessThanOrEqual
    blanking.constraint(0).comparison_value=iso_zone.values(var_num_to_blank).min()
    blanking.cell_mode=ValueBlankCellMode.AnyCorner
    print("Value blanking as been set in the 2D plot to eliminate cells at the periodic boundary of Theta. You may need to adjust this value slightly. Visit Plot>Blanking>Value Blanking.")


if __name__ == "__main__":
    axial_direction = input("Enter the axial direction [X,Y,or Z]:").upper()
    radius = float(input("Enter the radius value:"))
    print("Radius:", radius)

    # Compute the center based on an input zone.
    zone_name = input("Enter the reference zone name, to use to compute the center point (accepts wildcards *):")

    tp.session.connect()
    with tp.session.suspend():
        start = time.time()
        reference_zone = tp.active_frame().dataset.zone(zone_name)
        print("Reference zone:", reference_zone.name)
        center_point = (
            (reference_zone.values(0).max() + reference_zone.values(0).min()) / 2.
            ,(reference_zone.values(1).max() + reference_zone.values(1).min()) / 2.
            ,(reference_zone.values(2).max() + reference_zone.values(2).min()) / 2.
        )
        print("Center Point:", center_point)

        create_annular_slice(axial_direction, radius, center_point)
        print("Elapsed:", time.time()-start)

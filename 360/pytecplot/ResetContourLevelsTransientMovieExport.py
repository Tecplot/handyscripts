"""
This PyTecplot script updates the contour levels for each frame of a video and
exports it in .mp4 format.

In connected mode, it loops through the timesteps, changing the contour levels
for the Contour Group of interest based on the contour variable min/max of the
current timestep zone.
"""


import tecplot as tp
import os

# Set the following variables based on your specific data set
# Enter the numbers you find in the Tecplot "Contour & Multi-Coloring Details" dialog
contourGroup  = 1
variableIndex = 4

# Since Python starts counting at 0, decrement the user-specified values by 1
contourGroup  -= 1
variableIndex -= 1

# Connect to running Tecplot session with transient data
tp.session.connect()

frame = tp.active_frame()
dataset = frame.dataset
plot = frame.plot()

# Set the number of contour levels
num_levels = 11

# Path to folder
folder_path = os.getcwd()

with tp.session.suspend():
    # Creating animation file
    with tp.export.animation_mpeg4(os.path.join(folder_path,"transient_contour_reset.mp4")) as animation:
        # Loop through the solution times and reset the contour levels based on the timestep's max/min contour variable
        for i,t in enumerate(dataset.solution_times):
            # Set the frame's solution time
            plot.solution_time = t

            # Setting and showing contour variable for contour group
            tp.active_frame().plot().contour(contourGroup).variable_index=variableIndex
            tp.active_frame().plot().show_contour=True

            # Calculations for reseting contour levels per timestep
            cont_var = plot.contour(contourGroup).variable
            delta = ((cont_var.max()-cont_var.min())/num_levels) #contour level delta

            # Creating a list of contour level values
            cont_level_values = []
            for j in range(num_levels):
                curlevel = ((plot.contour(contourGroup).variable.min()) + (delta/2) + (j*delta))
                cont_level_values.append(round(curlevel,2))
            tp.active_frame().plot().contour(contourGroup).levels.reset_levels(cont_level_values)

            # Export an animation... in the tp.export.animation_mpeg4 context coupled with the following command
            print("Exporting image at t={}".format(t))
            animation.export_animation_frame()

            # Or you can export separate images...
            tp.export.save_png("image%04d.png"%(i))
print("Done")

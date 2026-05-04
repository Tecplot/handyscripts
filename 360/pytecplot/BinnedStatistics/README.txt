Example which uses scipy.stats.binned_statistics_2d to compute statistics on scatter point data and present the results on a 2D structured mesh.

Prerequisites:
1) Install 64-bit Python.  Python 3.5 or newer preferred
2) Install PyTecplot
3) Install numpy
4) Install scipy

Instructions for use:
1) Start Tecplot 360
2) Enable PyTecplot Connections via "Scripting->PyTecplot Connections...".
   Toggle on "Accept Connections"
3) Open converge_binned_statistics.lpk.  This layout plots the volume cell data as a 2D scatter plot with 'temp' on the X-axis and 'equiv_ratio' on the Y-axis.
4) In a command prompt, run binned_statistics_2d.py




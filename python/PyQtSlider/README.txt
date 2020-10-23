PyQt5 QSlider example.  This example shows the use of a slider to interpolate 
values between two datasets.

Prerequisites:
1) Install 64-bit Python.  Python 3.5 or newer preferred
2) Install PyTecplot
3) Install PyQt5: https://pypi.org/project/PyQt5/

Instructions for use:
1) Start Tecplot 360
2) Enable PyTecplot Connections via "Scripting->PyTecplot Connections...". 
   Toggle on "Accept Connections"
3) Run test-pyqt5-demo.py. Prefer launching as 'python -O test-pyqt5-demo.py'.  
   The '-O' flag runs Python in optimized mode and will run faster.
4) On the dialog that launches, press 'Load Data'.
5) Once the data are loaded, drag the slider back and forth to interpolate between Mach values.


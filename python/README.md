Tips for running the Python Scripts in this folder:

Running a Python script, from GitHub for example, has a couple prerequisites:
1.	You need a 64-bit version of Python 3 installed, such as Python 3.8, which is downloadable from https://www.python.org/downloads/
2.	You need to install PyTecplot.  Installation notes are here (Windows, but we also have Linux and Mac instructions): https://www.tecplot.com/docs/pytecplot/install.html#id2.  It should be as easy as typing ‘python –m pip install pytecplot’.  If you don’t have admin rights you may also have to include the ‘--user' flag: ‘python -m pip install --user pytecplot’
3.	Save the GitHub code to a file ending in “.py”
 
Once those pre-requisites are fulfilled, to run the script in connected mode: 
1.	Launch Tecplot 360 
2.	From the Scripting menu select “PyTecplot Connections…” and check the “Accept connections” toggle. 
3.	Open a command prompt 
4.	cd to the directory where you saved the script in step #3 above. 
5.	Run the PyTecplot script, for example:
        python <name_of_the_script.py>

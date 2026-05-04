import tecplot as tp
from tecplot.constant import *
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt


class Example(QtWidgets.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        loadDataButton = QtWidgets.QPushButton("Load Data")
        loadDataButton.clicked.connect(self.load_data)

        self.slider_label = QtWidgets.QLabel()
        
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.sliderValueChanged)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(loadDataButton)
        vbox.addWidget(self.slider_label)
        vbox.addWidget(self.slider)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 600, 0)
        self.setWindowTitle('Slider Demo')
        self.show()

    def load_data(self, *a):
        with tp.session.suspend():
            tp.new_layout()
            # Load the Mach 0.1 Dataset and capture the associated zones
            self.dataset = tp.data.load_tecplot("mach_0.1.plt")
            self.ds1 = list(self.dataset.zones())
            for z in self.ds1:
                z.solution_time = 0.1

            # Load the Mach 0.2 Dataset and capture the associated zones
            tp.data.load_tecplot("mach_0.2.plt")
            self.ds2 = list(self.dataset.zones())[len(self.ds1):]
            for z in self.ds2:
                z.solution_time = 0.2
            
            # Create a 'result' set of zones and capture the associated zones
            self.ds_result = self.dataset.copy_zones(self.ds1)
            for z in self.ds_result:
                z.solution_time = 0

            # Set up some default style
            plot = tp.active_frame().plot(PlotType.Cartesian3D)
            plot.activate()
            plot.show_contour = True
            plot.contour(0).levels.reset_levels([-1500, -1200, -900, -600, -300, 0, 300, 600, 900, 1200, 1500])
            plot.contour(0).colormap_name = 'Diverging - Blue/Red'
            plot.contour(0).colormap_filter.distribution=ColorMapDistribution.Continuous
            plot.contour(0).colormap_filter.continuous_min=-1500
            plot.contour(0).colormap_filter.continuous_max=1500

            plot.view.rotate_to_angles(115,115,-80)
            plot.view.position = (-65,33.5,-35.4)
            plot.view.width = 6
        
    def update_result_zones(self, percentage):
        # Do a linear interpolation between Mach 0.1 and Mach 0.2 and apply
        # the result to the result zones. Do this only for the surface zones
        # and for the 'Pressure' variable to save time
        with tp.session.suspend():
            for z1,z2,zresult in zip(self.ds1,self.ds2,self.ds_result):
                if z1.rank != 2:
                    continue
                v = z1.dataset.variable('Pressure')
                v1 = z1.values(v)[:]
                v2 = z2.values(v)[:]
                v3 = v1 + (v2 - v1) * percentage
                zresult.values(v)[:] = v3
            

    def sliderValueChanged(self, *a):
        v = self.slider.value()
        percentage = v/100
        self.update_result_zones(percentage)
        mach_min = 0.1
        mach_max = 0.2
        mach = mach_min + (mach_max - mach_min) * percentage
        self.slider_label.setText("Mach: {}".format(mach))

if __name__ == '__main__':
    tp.session.connect()
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

import sys
import time
import tempfile
import tecplot as tp
from tecplot.constant import *
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
import ColorBrewer_Linemap_Coloring as cbrewer


class LineMapUpdater(QtWidgets.QWidget):

    def __init__(self):
        super(LineMapUpdater, self).__init__()
        self.initUI()

    def initUI(self):
        self.zone_pattern_text = QtWidgets.QLineEdit()
        self.zone_pattern_text.setPlaceholderText("Enter zone name or wildcard pattern")
        #self.zone_pattern_text.textEdited.connect(self.zone_pattern_changed)

        self.zone_list = QtWidgets.QListWidget()
        self.zone_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.zone_list.itemSelectionChanged.connect(self.zone_list_changed)

        self.x_var_list = QtWidgets.QListWidget()
        self.x_var_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.x_var_list.clicked.connect(self.x_var_changed)

        self.y_var_list = QtWidgets.QListWidget()
        self.y_var_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.y_var_list.clicked.connect(self.y_var_changed)

        self.color_box = QtWidgets.QComboBox()
        self.color_box.currentIndexChanged.connect(self.color_palette_changed)
        colors = cbrewer.get_color_palettes()
        self.color_box.addItems(sorted(colors))

        self.select_button = QtWidgets.QPushButton("Select")
        self.select_button.clicked.connect(self.select_zones)
  
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        pattern_layout = QtWidgets.QHBoxLayout()
        pattern_layout.addWidget(QtWidgets.QLabel("Zone Pattern"))
        pattern_layout.addWidget(self.zone_pattern_text)
        pattern_layout.addWidget(self.select_button)
        layout.addLayout(pattern_layout)

        layout.addWidget(QtWidgets.QLabel("Zones"))
        layout.addWidget(self.zone_list)

        vars_layout = QtWidgets.QHBoxLayout()
        xvar_layout = QtWidgets.QVBoxLayout()
        xvar_layout.addWidget(QtWidgets.QLabel("X Variable"))
        xvar_layout.addWidget(self.x_var_list)

        yvar_layout = QtWidgets.QVBoxLayout()
        yvar_layout.addWidget(QtWidgets.QLabel("Y Variable"))
        yvar_layout.addWidget(self.y_var_list)
        vars_layout.addLayout(xvar_layout)
        vars_layout.addLayout(yvar_layout)
        
        layout.addLayout(vars_layout)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(QtWidgets.QLabel("Color Palette"))
        color_layout.addWidget(self.color_box)

        layout.addLayout(color_layout)
        self.setGeometry(300, 300, 600, 800)
        self.setWindowTitle('Quick Linemap Updater')

        self.reset_gui()

        self.show()

    def reset_gui(self):
        self.suspend_updates = True
        zone_names = tp.active_frame().dataset.zone_names
        self.zone_list.clear()
        self.zone_list.addItems(zone_names)

        variable_names = tp.active_frame().dataset.variable_names
        self.x_var_list.clear()
        self.y_var_list.clear()
        self.x_var_list.addItems(variable_names)
        self.y_var_list.addItems(variable_names)

        self.x_var_list.setCurrentRow(0)
        self.y_var_list.setCurrentRow(0)
        self.zone_list.setCurrentRow(0)

        self.suspend_updates = False

        # leave empty so we see the placeholder text
        #self.zone_pattern_text.setText(zone_names[0])

    def color_palette_changed(self, index):
        palette = self.color_box.currentText()
        with tp.session.suspend():
            frame = tp.active_frame()
            plot = frame.plot(PlotType.XYLine)
            plot.activate()
            cbrewer.setup_colors(plot.linemaps(), palette)

    def select_zones(self):
        self.zone_pattern_changed()

    def zone_pattern_changed(self):
        with tp.session.suspend():
            ds = tp.active_frame().dataset
            zone_pattern = self.zone_pattern_text.text()
            zones = list(ds.zones(zone_pattern))
            self.update_zones_to_plot(zones)
            zone_names = [z.name for z in zones]
            self.suspend_updates = True
            try:
                for row in range(self.zone_list.count()):
                    item = self.zone_list.item(row)
                    selected = item.text() in zone_names
                    item.setSelected(selected)
            finally:
                self.suspend_updates = False
            
   
    def create_linemaps(self, zones, xvar, yvar):
        """
        Build a macro file to create the new set of linemaps and execute it. This proved
        faster than using Plot.add_linemap(), unfortunately
        """
        x_var_num = xvar.index+1
        y_var_num = yvar.index+1
        cmd = "$!DeleteLineMaps\n"
        now = time.time()
        for mapnum,z in enumerate(zones):
            mapnum += 1
            cmd += f"""
                $!CreateLineMap 
                $!LineMap [{mapnum}]  
                  Name = '&DV& - &ZN&'
                  Assign 
                  {{ 
                    XAxisVar = {x_var_num}
                    YAxisVar = {y_var_num}
                    Zone = {z.index+1}
                  }}
                  Lines {{ LineThickness = 0.4 }}
                $!ActiveLineMaps += [{mapnum}]
                """
##        print("Constructed command:", time.time()-now)
        now = time.time()
        with tempfile.NamedTemporaryFile(suffix=".mcr", mode="w", delete=False) as f:
            f.write("#!MC 1410\n")
            f.write(cmd)
            f.flush()
            #print(f.name)
            tp.macro.execute_file(f.name)
##        print("Executed File:", time.time()-now)

##        now = time.time()
##        tp.macro.execute_command(cmd)
##        print("Executed command:", time.time()-now)


    def update_zones_to_plot(self, zones):
        with tp.session.suspend():
            frame = tp.active_frame()
            plot = frame.plot(PlotType.XYLine)
            plot.activate()
            x_var_name = self.x_var_list.currentItem().text()
            y_var_name = self.y_var_list.currentItem().text()
            ds = frame.dataset
            x_var = ds.variable(x_var_name)
            y_var = ds.variable(y_var_name)

            # Unfortunately, PyTecplot's add_linemap() function is too slow in connected mode
            # so we use this function when creates a macro file and executes it.
            self.create_linemaps(zones, x_var, y_var)

##            now = time.time()
##            plot.delete_linemaps()
##            for z in zones:
##                plot.add_linemap(name="&DV& - &ZN&", zone=z, x=x_var, y=y_var)
##            print(f"plot.add_linemap: {time.time()-now}")

            plot.view.fit()

    def zone_list_changed(self):
        if self.suspend_updates:
            return
        with tp.session.suspend():
            ds = tp.active_frame().dataset
            # Assumes that the zone list and zones in 360 are in the same order, which
            # is usually (but not always) the case. It's possible to have "unenabled" zones,
            # but this is a pretty rare scenario
            zones = [ds.zone(self.zone_list.row(item)) for item in self.zone_list.selectedItems()]
            self.update_zones_to_plot(zones)
        
    def update_axis_variable(self, which_axis, var_name):
        with tp.session.suspend():
            frame = tp.active_frame()
            plot = frame.plot(PlotType.XYLine)
            plot.activate()
            var = frame.dataset.variable(var_name)
            if which_axis == 'X':
                plot.linemaps().x_variable = var
            else:
                assert(which_axis == 'Y')
                plot.linemaps().y_variable = var
            plot.view.fit()

    def x_var_changed(self, qmodelindex):
        item = self.x_var_list.currentItem()
        var_name = item.text()
        self.update_axis_variable('X', var_name)

    def y_var_changed(self, qmodelindex):
        item = self.y_var_list.currentItem()
        var_name = item.text()
        self.update_axis_variable('Y', var_name)
        

if __name__ == '__main__':
    tp.session.connect()
    tp.session._tecutil_connector.client.processing_mode = tp.constant.TecUtilServerProcessingMode.Single
    app = QtWidgets.QApplication(sys.argv)
    ex = LineMapUpdater()
    sys.exit(app.exec_())

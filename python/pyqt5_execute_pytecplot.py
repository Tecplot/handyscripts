import sys
import os
import tempfile
import tecplot as tp
from PyQt5 import QtWidgets, QtGui
from subprocess import Popen, PIPE

class ExecutePyTecplot(QtWidgets.QWidget):
    def __init__(self):
        super(ExecutePyTecplot, self).__init__()
        self.initUI()

    def initUI(self):
        self.python_command_textEdit = QtWidgets.QTextEdit()

        boilerPlate = """import tecplot as tp
from tecplot.constant import *
tp.session.connect()
frame = tp.active_frame()
plot = frame.plot()
dataset = frame.dataset
"""

        self.python_command_textEdit.setPlainText(boilerPlate)

        addExecutePyTecplot_Button = QtWidgets.QPushButton("Execute")
        addExecutePyTecplot_Button.clicked.connect(self.execute_python_command_CB)

        self.result_textEdit = QtWidgets.QTextEdit()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.python_command_textEdit)
        vbox.addWidget(addExecutePyTecplot_Button)
        vbox.addWidget(self.result_textEdit)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 1600, 1200)
        self.setWindowTitle('PyTecplot Runner')
        self.show()

    def execute_python_command_CB(self, *a):
        cmd = self.python_command_textEdit.toPlainText()
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(cmd.encode('utf8'))
            temp_file.flush()
            p = Popen(['python', '-O', temp_file.name], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"SomeString")
            rc = p.returncode
            if rc == 0:
                self.result_textEdit.setPlainText(output.decode('utf8'))
            else:
                self.result_textEdit.setPlainText(err.decode('utf8'))
        except Exception as e:
            self.result_textEdit.setPlainText(str(e))
        finally:
            temp_file.close()
            os.unlink(temp_file.name)
        

if __name__ == '__main__':
    tp.session.connect()
    app = QtWidgets.QApplication(sys.argv)
    ex = ExecutePyTecplot()
    res = app.exec_()
    sys.exit(res)

import sys
import os
import tempfile
import tecplot as tp
from PyQt5 import QtWidgets, QtGui

class ExecuteMacroCommand(QtWidgets.QWidget):
    def __init__(self):
        super(ExecuteMacroCommand, self).__init__()
        self.initUI()

    def initUI(self):
        self.macro_command_textEdit = QtWidgets.QTextEdit()
        self.macro_command_textEdit.setPlainText("#!MC 1410")

        addExecuteMacroCommand_Button = QtWidgets.QPushButton("Execute")
        addExecuteMacroCommand_Button.clicked.connect(self.execute_macro_command_CB)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.macro_command_textEdit)
        vbox.addWidget(addExecuteMacroCommand_Button)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Macro Command Runner')
        self.show()

    def execute_macro_command_CB(self, *a):
        cmd = self.macro_command_textEdit.toPlainText()
        try: 
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mcr")
            temp_file.write(cmd.encode('utf8'))
            temp_file.flush()
            tp.macro.execute_file(temp_file.name)
        except Exception as e:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setWindowTitle("Error")
            if str(e):
                error_dialog.setText("Error: {}".format(str(e)))
            else:
                error_dialog.setText("Error:\nNo error details available. ")
            error_dialog.exec_()
        finally:
            temp_file.close()
            os.unlink(temp_file.name)

if __name__ == '__main__':
    try:
        tp.session.connect()
        app = QtWidgets.QApplication(sys.argv)
        ex = ExecuteMacroCommand()
        res = app.exec_()
        sys.exit(res)
    except Exception as e:
        log("Error")
        log(str(e))
    

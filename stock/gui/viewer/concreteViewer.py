from stock.gui.viewer.viewer import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets


class ConcreteViewer(Ui_MainWindow):

    def __init__(self):
        super().__init__()

    def setupUi(self, main_window):
        super().setupUi(main_window)
        self.infoTab.

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider
import sys
from outputWindow import OutputWindow

class MyWindow(QMainWindow):
    def open_output_window(self):
        # Create a new instance of the output window
        self.output_window = OutputWindow()
        # Show the output window
        self.output_window.show()

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.ui.applyButton.clicked.connect(self.open_output_window)


from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider
import sys


class OutputWindow(QMainWindow):  
      
    def __init__(self):
        super(OutputWindow, self).__init__()
        self.ui = uic.loadUi("window2.ui", self)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle('Output Screen')
from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider
import sys
from PyQt5.QtGui import QPixmap


class OutputWindow(QMainWindow):  
      
    def __init__(self):
        super(OutputWindow, self).__init__()
        self.ui = uic.loadUi("window2.ui", self)
        self.setWindowTitle('Output Screen')

    def addimage(self,key,QImage):
        if key == 1:
            self.ui.output_1.clear()
            self.ui.output_1.setPixmap(QPixmap(QImage))
        elif key == 2:
            self.ui.output_2.clear()
            self.ui.output_2.setPixmap(QPixmap(QImage))
    
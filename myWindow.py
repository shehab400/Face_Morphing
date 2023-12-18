from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap , QImage
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider, QFileDialog
import sys
import matplotlib.pyplot as plt
from outputWindow import OutputWindow
import numpy as np

count = 0

class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.ui.applyButton.clicked.connect(self.open_output_window)
        self.ui.fixedImage1.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage1)
        self.ui.fixedImage2.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage2)
        self.ui.fixedImage3.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage3)
        self.ui.fixedImage4.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage4)

    def open_output_window(self):
        global count
        # Create a new instance of the output window
        if count == 0:
            self.output_window = OutputWindow()
            # Show the output window
            self.output_window.show()
            count = 1 
        else: 
            count = 0
            pass

    def imageDisplay(self , Qlabel):
        fname = QFileDialog.getOpenFileName(self, "open fie", "D:\College\College Year 3 (Junior)\DSP\Task 4\Face_Morphing\Images", "All Files (*)" )
        # self.path

        # self.label = self.findChild(Qlabel, "Qlabel")

        original_image = QImage(fname[0])
        grayscale_image = original_image.convertToFormat(QImage.Format_Grayscale8)
        
        self.pixmap = QPixmap.fromImage(grayscale_image)
        Qlabel.setPixmap(self.pixmap)

        # self.raw_data = plt.imread(self.path)
        # self.raw_data = self.raw_data.astype('float32')
        # self.raw_data /= 255


        # # Get size
        # self.shape = self.raw_data.shape
        # self.width = self.shape[0]
        # self.height = self.shape[1]
        
        # # Fourier FFT
        # self.fft = np.fft.fft2(self.raw_data)
        # # Get magnitude
        # self.magnitude = np.abs(self.fft)
        # # Get phase
        # self.phase = np.angle(self.fft)
        # # Get real
        # self.real = np.real(self.fft)
        # # Get imag
        # self.imaginary = np.imag(self.fft)


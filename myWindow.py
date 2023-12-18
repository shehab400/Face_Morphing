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
from Image import *
count = 0

Images=[]
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.ui.applyButton.clicked.connect(self.open_output_window)
        self.ui.fixedImage1.mousePressEvent = lambda event: self.removeImage(1,self.ui.fixedImage1)
        self.ui.fixedImage2.mousePressEvent = lambda event: self.removeImage(2,self.ui.fixedImage2)
        self.ui.fixedImage3.mousePressEvent = lambda event: self.removeImage(3,self.ui.fixedImage3)
        self.ui.fixedImage4.mousePressEvent = lambda event: self.removeImage(4,self.ui.fixedImage4)
        self.ui.fixedImage1.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage1,1)
        self.ui.fixedImage2.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage2,2)
        self.ui.fixedImage3.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage3,3)
        self.ui.fixedImage4.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage4,4)

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

    def imageDisplay(self , Qlabel,imglabel):
        img=Image()
        img.imagelabel=imglabel
        filename = QtWidgets.QFileDialog.getOpenFileName()
        img.path = filename[0]
        # self.path
        # self.label = self.findChild(Qlabel, "Qlabel")
        original_image = QImage(img.path)
        grayscale_image = original_image.convertToFormat(QImage.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(grayscale_image)
        Qlabel.setPixmap(self.pixmap)

        raw_data = plt.imread(img.path)
        raw_data = raw_data.astype('float32')
        raw_data /= 255
        img.raw_data=raw_data
        # Get size
        img.shape = img.raw_data.shape
        img.width = img.shape[0]
        img.height = img.shape[1]
        
        # # Fourier FFT
        img.fft = np.fft.fft2(img.raw_data)
        # # Get magnitude
        img.magnitude = np.abs(img.fft)
        # # Get phase
        img.phase = np.angle(img.fft)
        # # Get real
        img.real = np.real(img.fft)
        # # Get imag
        img.imaginary = np.imag(img.fft)
        Images.append(img)
        print(len(Images)) ############### need to create remove image function to update length of images array

    def removeImage(self,imglabel,Qlabel):
        if imglabel==0:
            return
        else:
            for index, image in enumerate(Images):
              if image.imagelabel ==imglabel :
                 Qlabel.clear()
                 Images.pop(index)
                 print(len(Images))
            
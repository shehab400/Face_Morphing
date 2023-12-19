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
mode=""
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.ui.applyButton.clicked.connect(self.open_output_window)
        self.ui.comboBox_1.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_1,1))
        self.ui.comboBox_2.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_2,2))
        self.ui.comboBox_3.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_3,3))
        self.ui.comboBox_4.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_4,4))
        self.ui.fixedImage1.mousePressEvent  = lambda event: self.removeImage(1,self.ui.fixedImage1,self.ui.changedImage1)
        self.ui.fixedImage2.mousePressEvent  = lambda event: self.removeImage(2,self.ui.fixedImage2,self.ui.changedImage2)
        self.ui.fixedImage3.mousePressEvent  = lambda event: self.removeImage(3,self.ui.fixedImage3,self.ui.changedImage3)
        self.ui.fixedImage4.mousePressEvent  = lambda event: self.removeImage(4,self.ui.fixedImage4,self.ui.changedImage4)
        self.ui.fixedImage1.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage1,self.ui.changedImage1,self.ui.comboBox_1,1)
        self.ui.fixedImage2.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage2,self.ui.changedImage2,self.ui.comboBox_2,2)
        self.ui.fixedImage3.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage3,self.ui.changedImage3,self.ui.comboBox_3,3)
        self.ui.fixedImage4.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.ui.fixedImage4,self.ui.changedImage4,self.ui.comboBox_4,4)
        self.ui.comboBox_1.addItem("Magnitude")
        self.ui.comboBox_1.addItem("Phase")
        self.ui.comboBox_1.addItem("Real")
        self.ui.comboBox_1.addItem("Imaginary")
        self.ui.comboBox_2.addItem("Magnitude")
        self.ui.comboBox_2.addItem("Phase")
        self.ui.comboBox_2.addItem("Real")
        self.ui.comboBox_2.addItem("Imaginary")
        self.ui.comboBox_3.addItem("Magnitude")
        self.ui.comboBox_3.addItem("Phase")
        self.ui.comboBox_3.addItem("Real")
        self.ui.comboBox_3.addItem("Imaginary")
        self.ui.comboBox_4.addItem("Magnitude")
        self.ui.comboBox_4.addItem("Phase")
        self.ui.comboBox_4.addItem("Real")
        self.ui.comboBox_4.addItem("Imaginary")
        # self.ui.comboBox_5.addItem("Imaginary")
        # self.ui.comboBox_5.addItem("Magnitude")
        # self.ui.comboBox_5.addItem("Phase")
        # self.ui.comboBox_5.addItem("Real")
        # self.ui.comboBox_6.addItem("Magnitude")
        # self.ui.comboBox_6.addItem("Phase")
        # self.ui.comboBox_6.addItem("Real")
        # self.ui.comboBox_6.addItem("Imaginary")
        # self.ui.comboBox_8.addItem("Magnitude")
        # self.ui.comboBox_7.addItem("Phase")
        # self.ui.comboBox_7.addItem("Real")
        # self.ui.comboBox_7.addItem("Imaginary")
        # self.ui.comboBox_8.addItem("Magnitude")
        # self.ui.comboBox_8.addItem("Phase")
        # self.ui.comboBox_8.addItem("Real")
        # self.ui.comboBox_8.addItem("Imaginary")
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

    def chooseMood_1(self):
        Index = self.comboBox.currentIndex()
        if Index == 1:
            pass

    def imageDisplay(self,Qlabel,Qlabel2,QComboBox,imglabel):
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
        print(len(Images)) # need to create remove image function to update length of images array
        self.setMode()
        self.plottingChosenComponents(img,QComboBox.currentText(),Qlabel2)
    def removeImage(self,imglabel,Qlabel,Qlabel2):
        if imglabel==0:
            return
        else:
            for index, image in enumerate(Images):
             if image.imagelabel ==imglabel :
                 Qlabel.clear()
                 Qlabel2.clear()
                 Images.pop(index)
                 print(len(Images))
            
    def setMode(self):
       global mode
       if  self.ui.comboBox.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_5.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_6.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_7.currentText() in ["Real", "Imaginary"]:
           mode= 'real-imag' 
           print(mode)
       if   self.ui.comboBox.currentText() in ["Magnitude", "Phase"]  and self.ui.comboBox_5.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_6.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_7.currentText() in ["Magnitude", "Phase"]:
           mode= 'mag-phase'
           print(mode)
    def plottingChosenComponents(self,img,component,Qlabel):
        if component in ["Magnitude"] :
            magnitude_spectrum = img.magnitude
            magnitude_spectrum_log = np.log1p(magnitude_spectrum)
            magnitude_spectrum_normalized = (magnitude_spectrum_log - np.min(magnitude_spectrum_log)) / (np.max(magnitude_spectrum_log) - np.min(magnitude_spectrum_log))
            plt.imsave('test.png', magnitude_spectrum_normalized, cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
        if component in ["Real"] :
            real_part_normalized = (img.real - np.min(img.real)) / (np.max(img.real) - np.min(img.real))
            plt.imsave('test.png',real_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
        if component in ["Phase"] :
            phase_part_normalized = (img.phase - np.min(img.phase)) / (np.max(img.phase) - np.min(img.phase))
            plt.imsave('test.png',phase_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
        if component in ["Imaginary"] :
            imaginary_part_normalized = (img.imaginary - np.min(img.imaginary)) / (np.max(img.imaginary) - np.min(img.imaginary))
            plt.imsave('test.png',imaginary_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8) 

        Qlabel.setPixmap(QPixmap(grayscale_image))
    def updatingComboBox(self,QComboBox,flag):
        if len(Images)>0:
            if flag==1:
                label=self.ui.changedImage1
                img=Images[0]
                component=QComboBox.currentText()
                self.plottingChosenComponents(img,component,label)
        
            if flag==2:
                label=self.ui.changedImage2
                img=Images[1]
                component=QComboBox.currentText()
                self.plottingChosenComponents(img,component,label)
            if flag==3:
                label=self.ui.changedImage3
                img=Images[2]
                component=QComboBox.currentText()
                self.plottingChosenComponents(img,component,label)
            if flag==4:
                label=self.ui.changedImage4
                img=Images[3]
                component=QComboBox.currentText()
                self.plottingChosenComponents(img,component,label)
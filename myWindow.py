from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot,  Qt
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap , QImage, QColor, QPainter, QBrush
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider, QFileDialog ,QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton, QColorDialog
import sys
import matplotlib.pyplot as plt
import numpy as np
from Image import *
from matplotlib.colors import Normalize

from outputWindow import *
count = 0

Images=[]
filteredImages = []
mode=""
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.ui.applyButton.clicked.connect(self.open_output_window)
        self.rect_items = []
        self.overlay_color = QColor(255, 0, 0, 100)
        for combo in [self.ui.comboBox_1,self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
            combo.addItems(["Magnitude","Phase","Real","Imaginary"])
        self.updatingComboBox(self.ui.comboBox_1,1)   
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

        for combo in [self.ui.comboBox_1,self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
            combo.addItems(["Magnitude","Phase","Real","Imaginary"])
       
        for slider in [self.ui.horizontalSlider,self.ui.horizontalSlider_2,self.ui.horizontalSlider_3,self.ui.horizontalSlider_4]:
             slider.valueChanged.connect(lambda value, mode=mode: self.mixing(value))

        self.Inner_radio.toggled.connect(self.select_region)
        self.Outer_radio.toggled.connect(self.select_region)



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
    
    def select_region(self):
        if self.Inner_radio.isChecked():
            self.add_rectangle(inner=True)
        elif self.Outer_radio.isChecked():
            self.add_rectangle(inner=False)

    # def add_rectangle(self, Qlabel, inner=True):
    #     for img in filteredImages:
    #         # Get image dimensions
    #         width = img.width()
    #         height = img.height()

    #         # Create a QPainter to draw on the image
    #         painter = QPainter(img)
    #         painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    #         # Define a transparent color for highlighting
    #         highlight_color = QColor(255, 0, 0, 128)  # Red with 50% transparency

    #         if inner:
    #             # Highlight the inner half of the image
    #             painter.fillRect(0, 0, width / 2, height, highlight_color)
    #         else  :
    #             # Highlight the outer half of the image
    #             painter.fillRect(width / 2, 0, width / 2, height, highlight_color)

    #         painter.end()
            
    #         Qlabel.changedImage1.setPixmap(QPixmap(img))
    
    def setMode(self):
       global mode
       if  self.ui.comboBox_1.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_2.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_3.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_4.currentText() in ["Real", "Imaginary"]:
           mode= 'real-imag' 
           print(mode)
       if   self.ui.comboBox_1.currentText() in ["Magnitude", "Phase"]  and self.ui.comboBox_2.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_3.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_4.currentText() in ["Magnitude", "Phase"]:
           mode= 'mag-phase'
           print(mode)

    def plottingChosenComponents(self,img,component,Qlabel):
        if component in ["Magnitude"] :
            magnitude_spectrum = img.magnitude
            magnitude_spectrum_log = np.log1p(magnitude_spectrum)
            magnitude_spectrum_normalized = (magnitude_spectrum_log - np.min(magnitude_spectrum_log)) / (np.max(magnitude_spectrum_log) - np.min(magnitude_spectrum_log))
            plt.imsave('test.png', magnitude_spectrum_normalized, cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages.append(grayscale_image)
        if component in ["Real"] :
            real_part_normalized = (img.real - np.min(img.real)) / (np.max(img.real) - np.min(img.real))
            plt.imsave('test.png',real_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages.append(grayscale_image)
        if component in ["Phase"] :
            phase_part_normalized = (img.phase - np.min(img.phase)) / (np.max(img.phase) - np.min(img.phase))
            plt.imsave('test.png',phase_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages.append(grayscale_image)
        if component in ["Imaginary"] :
            imaginary_part_normalized = (img.imaginary - np.min(img.imaginary)) / (np.max(img.imaginary) - np.min(img.imaginary))
            plt.imsave('test.png',imaginary_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8) 
            filteredImages.append(grayscale_image)
        Qlabel.setPixmap(QPixmap(grayscale_image))

    def updatingComboBox(self,QComboBox,flag):
        component=QComboBox.currentText()
        if flag == 1:
            if component in ["Magnitude","Phase"]:
                for combo in [self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
                    combo.clear()
                    combo.addItems(["Magnitude","Phase"])
            else:
                for combo in [self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
                    combo.clear()
                    combo.addItems(["Real","Imaginary"])
        if len(Images)>0:
            if flag==1:
                label=self.ui.changedImage1
                img=Images[0]
                self.plottingChosenComponents(img,component,label)        
            if flag==2:
                label=self.ui.changedImage2
                img=Images[1]
                self.plottingChosenComponents(img,component,label)
            if flag==3:
                label=self.ui.changedImage3
                img=Images[2]
                self.plottingChosenComponents(img,component,label)
            if flag==4:
                label=self.ui.changedImage4
                img=Images[3]
                component=QComboBox.currentText()
                self.plottingChosenComponents(img,component,label)
                
    def chooseComponent(self, type, ratio,img):
        if type == "Magnitude":
            return img.magnitude * ratio
        elif type == "Phase":
            return np.exp(1j * img.phase* ratio)
        elif type == "Real":
            return img.real * ratio
        elif type == "Imaginary":
            return (1j* img.imaginary)* ratio 
        
        
        
    def mixing(self,value):
      ratio1=self.ui.horizontalSlider.value()/100
      ratio2=self.ui.horizontalSlider_2.value()/100
      ratio3=self.ui.horizontalSlider_3.value()/100
      ratio4=self.ui.horizontalSlider_4.value()/100
      self.setMode()
      global mode
      print(mode)
      if(len(Images)>0):
        # firstcomponent=self.chooseComponent(type1,ratio1,Images[0])
        # secoundcomponent=self.chooseComponent(type2,ratio2,Images[1])
        # thirdcomponent=self.chooseComponent(type3,ratio3,Images[2])
        # fourthcomponent=self.chooseComponent(type4,ratio4,Images[3])
        if(mode=='mag-phase'):
        
            mixed_magnitude = np.zeros_like(Images[0].magnitude,np.float64)
            mixed_phase = np.ones_like(Images[0].phase,dtype=np.complex128)
            if self.ui.comboBox_1.currentText()=="Magnitude":
                mixed_magnitude =Images[0].magnitude * ratio1
            else:
                mixed_phase = np.exp(1j * Images[0].phase)* ratio1

            if  self.ui.comboBox_2.currentText()=="Magnitude":
                mixed_magnitude +=Images[1].magnitude * ratio2
            else:
                mixed_phase += np.exp(1j * Images[1].phase)* ratio2

            if self.ui.comboBox_3.currentText()=="Magnitude":
                mixed_magnitude +=Images[2].magnitude * ratio3
            else:
                mixed_phase +=np.exp(1j * Images[2].phase)*ratio3

            if self.ui.comboBox_4.currentText()=="Magnitude":
               mixed_magnitude +=Images[3].magnitude * ratio4
            else:
               mixed_phase+= np.exp(1j * Images[3].phase)* ratio4
            if np.max(np.angle(mixed_phase)) == 0:
                
                avg_mixed_image = (mixed_magnitude)
                # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                final_mixed_image = np.fft.ifft2(avg_mixed_image)
            elif(np.max(mixed_magnitude==0)):
                avg_mixed_image = (mixed_phase)
                # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                final_mixed_image = np.fft.ifft2(avg_mixed_image)
            else:
                avg_mixed_image = (mixed_magnitude *  mixed_phase)
                # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                final_mixed_image = np.fft.ifft2(avg_mixed_image)
            if (np.max(final_mixed_image)>1):
                final_mixed_image=final_mixed_image/np.max(final_mixed_image)
            plt.imsave('test1.png',np.abs(final_mixed_image) , cmap='gray')
            # grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8) 
            
                        
        elif(mode=='real-imag'):
            
            mixed_imaginary= np.zeros_like(Images[0].imaginary)
            mixed_real = np.ones_like(Images[0].real)
            if self.ui.comboBox_1.currentText()=="real":
                 mixed_real =Images[0].real * ratio1
            else:
                mixed_imaginary =(1j* Images[0].imaginary)* ratio1

            if  self.ui.comboBox_2.currentText()=="real":
                 mixed_real +=Images[1].real * ratio2
            else:
                mixed_imaginary += (1j* Images[1].imaginary)* ratio2

            if self.ui.comboBox_3.currentText()=="real":
                 mixed_real +=Images[2].real * ratio3
            else:
                mixed_imaginary +=(1j* Images[2].imaginary)* ratio3

            if self.ui.comboBox_4.currentText()=="real":
                 mixed_real +=Images[3].real * ratio4
            else:
                mixed_imaginary+=(1j* Images[3].imaginary)* ratio4
            
                
            avg_mixed_image = ( mixed_real + mixed_imaginary)
            # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
            final_mixed_image = np.fft.ifft2(avg_mixed_image)
          
            if (np.max(final_mixed_image)>1):
                final_mixed_image=final_mixed_image/np.max(final_mixed_image)
            plt.imsave('test2.png',np.abs(final_mixed_image) , cmap='gray')
            # grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8)

                self.plottingChosenComponents(img,component,label)


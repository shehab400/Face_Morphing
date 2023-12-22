from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot,  Qt,QRect
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap , QImage, QColor, QPainter, QBrush
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QRubberBand,QApplication,QMainWindow,QVBoxLayout,QPushButton,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider, QFileDialog ,QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton, QColorDialog
import sys
import matplotlib.pyplot as plt
import numpy as np
from Image import *
from matplotlib.colors import Normalize
from QExampleLabel import *
from outputWindow import *

count = 0

Images=[]
image1=Image()
image1.type=0
image2=Image()
image2.type=0
image3=Image()
image3.type=0
image4=Image()
image4.type=0
Images.append(image1)
Images.append(image2)
Images.append(image3)
Images.append(image4)
filteredImages = Images.copy()
mode=""
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.croppedImages = []
        self.fixed1 = QExampleLabel(self,1)
        self.fixed2 = QExampleLabel(self,2)
        self.fixed3 = QExampleLabel(self,3)
        self.fixed4 = QExampleLabel(self,4)
        self.changed1 = QExampleLabel(self,1)
        self.changed2 = QExampleLabel(self,2)
        self.changed3 = QExampleLabel(self,3)
        self.changed4 = QExampleLabel(self,4)
        self.changed1.setIsCropable(True)
        self.output_window = OutputWindow()
        self.ui.applyButton.clicked.connect(self.open_output_window)
        self.ui.widget.layout().addWidget(self.fixed1)
        self.ui.widget_2.layout().addWidget(self.fixed2)
        self.ui.widget_3.layout().addWidget(self.fixed3)
        self.ui.widget_4.layout().addWidget(self.fixed4)
        self.ui.widget_5.layout().addWidget(self.changed1)
        self.ui.widget_6.layout().addWidget(self.changed2)
        self.ui.widget_7.layout().addWidget(self.changed3)
        self.ui.widget_8.layout().addWidget(self.changed4)
        self.ui.radioButton.setChecked(True)
        self.ui.Inner_radio.setChecked(True)
        self.isInner = True
        self.overlay_color = QColor(255, 0, 0, 100)
        for combo in [self.ui.comboBox_1,self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
            combo.addItems(["Magnitude","Phase","Real","Imaginary"])
        self.updatingComboBox(self.ui.comboBox_1,1)   
        self.ui.comboBox_1.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_1,1))
        self.ui.comboBox_2.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_2,2))
        self.ui.comboBox_3.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_3,3))
        self.ui.comboBox_4.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_4,4))
        self.ui.widget.mousePressEvent  = lambda event: self.removeImage(1,self.fixed1,self.changed1)
        self.ui.widget_2.mousePressEvent  = lambda event: self.removeImage(2,self.fixed2,self.changed2)
        self.ui.widget_3.mousePressEvent  = lambda event: self.removeImage(3,self.fixed3,self.changed3)
        self.ui.widget_4.mousePressEvent  = lambda event: self.removeImage(4,self.fixed4,self.changed4)
        #self.fixed1.mousePressEvent = lambda event: self.mousePressEvent(self.ui.fixedImage1)

        self.ui.fixedImage1.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.fixed1,self.changed1,self.ui.comboBox_1,1)
        self.ui.fixedImage2.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.fixed2,self.changed2,self.ui.comboBox_2,2)
        self.ui.fixedImage3.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.fixed3,self.changed3,self.ui.comboBox_3,3)
        self.ui.fixedImage4.mouseDoubleClickEvent =lambda event: self.imageDisplay(self.fixed4,self.changed4,self.ui.comboBox_4,4)

        # for slider in [self.ui.horizontalSlider,self.ui.horizontalSlider_2,self.ui.horizontalSlider_3,self.ui.horizontalSlider_4]:
        #      slider.valueChanged.connect(lambda value, mode=mode: self.mixing(value))
        self.radioButton.toggled.connect(self.whichoutput)
        self.radioButton_2.toggled.connect(self.whichoutput)
        self.Inner_radio.toggled.connect(self.select_region)
        self.Outer_radio.toggled.connect(self.select_region)


        self.output = 1
        self.BC = None



    def open_output_window(self):
        global count
        # Create a new instance of the output window
        if count == 0:
            # Show the output window
            self.mixing()
            self.output_window.show()
            count = 1 
        else: 
            count = 0
            pass

    # def mousePressEvent(self,Qlabel):
    #     Qlabel.

    # def mouseMoveEvent (self, eventQMouseEvent):
    #     self.ui.fixedImage1.currentQRubberBand.setGeometry(QRect(self.ui.fixedImage1.originQPoint, eventQMouseEvent.pos()).normalized())
        
    # def mouseReleaseEvent (self, eventQMouseEvent):
    #     self.ui.fixedImage1.currentQRubberBand.hide()
    #     currentQRect = self.ui.fixedImage1.currentQRubberBand.geometry()
    #     self.ui.fixedImage1.currentQRubberBand.deleteLater()
    #     cropQPixmap = self.ui.fixedImage1.pixmap().copy(currentQRect)
    #     cropQPixmap.save('output.png')

    def imageInitializer(self,path,imglabel):
        img = Image()
        img.imagelabel=imglabel
        img.path = path
        # self.path
        # self.label = self.findChild(Qlabel, "Qlabel")
        original_image = QImage(img.path)
        grayscale_image = original_image.convertToFormat(QImage.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(grayscale_image)

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
        
        return img,self.pixmap,grayscale_image

    def imageDisplay(self,Qlabel,Qlabel2,QComboBox,imglabel):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        path = filename[0]
        img,self.pixmap,grayscale_image = self.imageInitializer(path,imglabel)
        Qlabel.setImage(self.pixmap,grayscale_image)

        Images[img.imagelabel-1] = img
        print(img.imagelabel)

        # print(len(Images)) # need to create remove image function to update length of images array
        self.croppedImages = Images.copy()
        for changed in [self.changed1,self.changed2,self.changed3,self.changed4]:
            changed.resetRubberBand()
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
            self.isInner = True
        elif self.Outer_radio.isChecked():
            self.isInner = False
            
    def selectBC(self):
        if self.brightness_radio.isChecked():
            self.BC = 1
        if self.contrast_radio.isChecked():
            self.BC = 2

    def whichoutput(self):
        if self.radioButton.isChecked():
            self.output = 1
        if self.radioButton_2.isChecked():
           self.output = 2
            
    def setMode(self):
       global mode
       if  self.ui.comboBox_1.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_2.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_3.currentText() in ["Real", "Imaginary"] and self.ui.comboBox_4.currentText() in ["Real", "Imaginary"]:
           mode= 'real-imag' 
           print(mode)
       if   self.ui.comboBox_1.currentText() in ["Magnitude", "Phase"]  and self.ui.comboBox_2.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_3.currentText() in ["Magnitude", "Phase"] and self.ui.comboBox_4.currentText() in ["Magnitude", "Phase"]:
           mode= 'mag-phase'
           print(mode)

    def plottingChosenComponents(self,img,component,Qlabel):
        global grayscale_image
        if component in ["Magnitude"] :
            magnitude_spectrum = img.magnitude
            magnitude_spectrum_log = np.log1p(magnitude_spectrum)
            magnitude_spectrum_normalized = (magnitude_spectrum_log - np.min(magnitude_spectrum_log)) / (np.max(magnitude_spectrum_log) - np.min(magnitude_spectrum_log))
            plt.imsave('test.png', magnitude_spectrum_normalized, cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Real"] :
            real_part_normalized = (img.real - np.min(img.real)) / (np.max(img.real) - np.min(img.real))
            plt.imsave('test.png',real_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Phase"] :
            phase_part_normalized = (img.phase - np.min(img.phase)) / (np.max(img.phase) - np.min(img.phase))
            plt.imsave('test.png',phase_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8)
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Imaginary"] :
            imaginary_part_normalized = (img.imaginary - np.min(img.imaginary)) / (np.max(img.imaginary) - np.min(img.imaginary))
            plt.imsave('test.png',imaginary_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png').convertToFormat(QImage.Format_Grayscale8) 
            filteredImages[img.imagelabel-1] = grayscale_image
        Qlabel.setImage(QPixmap(grayscale_image),grayscale_image)

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
        if Images[flag-1].type!=0:
            if flag==1:
                label=self.changed1
                img=Images[0]
                self.plottingChosenComponents(img,component,label)        
            if flag==2:
                label=self.changed2
                img=Images[1]
                self.plottingChosenComponents(img,component,label)
            if flag==3:
                label=self.changed3
                img=Images[2]
                self.plottingChosenComponents(img,component,label)
            if flag==4:
                label=self.changed4
                img=Images[3]
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
          
    def mixing(self):
      ratio1=self.ui.horizontalSlider.value()/100
      ratio2=self.ui.horizontalSlider_2.value()/100
      ratio3=self.ui.horizontalSlider_3.value()/100
      ratio4=self.ui.horizontalSlider_4.value()/100
      Rect = self.changed1.Rect

      if self.isInner == True:
        if Images[0].type!=0:
            self.changed1.getCropped(Rect)
            img,pixmap,grayscale_image = self.imageInitializer('output1.png',1)
            self.croppedImages[0]=img
        if Images[1].type!=0:
            self.changed2.getCropped(Rect)
            img,pixmap,grayscale_image = self.imageInitializer('output2.png',2)
            self.croppedImages[1]=img
        if Images[2].type!=0:
            self.changed3.getCropped(Rect)
            img,pixmap,grayscale_image = self.imageInitializer('output3.png',3)
            self.croppedImages[2]=img
        if Images[3].type!=0:
            self.changed4.getCropped(Rect)
            img,pixmap,grayscale_image = self.imageInitializer('output4.png',4)
            self.croppedImages[3]=img
      elif self.isInner == False:
        if Rect == QRect(QPoint(0,0),QtCore.QSize()):
            pass
        else:
            if Images[0].type!=0:
                self.changed1.getCropped(Rect)
            if Images[1].type!=0:
                pass
            if Images[2].type!=0:
                pass
            if Images[3].type!=0:
                pass

      self.setMode()
      global mode
      print(mode)
      if all(img.type != 0 for img in Images):
        # firstcomponent=self.chooseComponent(type1,ratio1,Images[0])
        # secoundcomponent=self.chooseComponent(type2,ratio2,Images[1])
        # thirdcomponent=self.chooseComponent(type3,ratio3,Images[2])
        # fourthcomponent=self.chooseComponent(type4,ratio4,Images[3])
        if(mode=='mag-phase'):
        
            mixed_magnitude = np.zeros_like(self.croppedImages[0].magnitude,np.float64)
            mixed_phase = np.ones_like(self.croppedImages[0].phase,dtype=np.complex128)
            if self.ui.comboBox_1.currentText()=="Magnitude":
                mixed_magnitude =self.croppedImages[0].magnitude * ratio1
            else:
                mixed_phase = np.exp(1j * self.croppedImages[0].phase)* ratio1

            if  self.ui.comboBox_2.currentText()=="Magnitude":
                mixed_magnitude +=self.croppedImages[1].magnitude * ratio2
            else:
                mixed_phase += np.exp(1j * self.croppedImages[1].phase)* ratio2

            if self.ui.comboBox_3.currentText()=="Magnitude":
                mixed_magnitude +=self.croppedImages[2].magnitude * ratio3
            else:
                mixed_phase +=np.exp(1j * self.croppedImages[2].phase)*ratio3

            if self.ui.comboBox_4.currentText()=="Magnitude":
               mixed_magnitude +=self.croppedImages[3].magnitude * ratio4
            else:
               mixed_phase+= np.exp(1j * self.croppedImages[3].phase)* ratio4
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
            grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8)
            self.output_window.addimage(self.output,grayscale_image)
            
                        
        elif(mode=='real-imag'):
            
            mixed_imaginary= np.zeros_like(self.croppedImages[0].imaginary)
            mixed_real = np.ones_like(self.croppedImages[0].real)
            if self.ui.comboBox_1.currentText()=="real":
                 mixed_real =self.croppedImages[0].real * ratio1
            else:
                mixed_imaginary =(1j* self.croppedImages[0].imaginary)* ratio1

            if  self.ui.comboBox_2.currentText()=="real":
                 mixed_real +=self.croppedImages[1].real * ratio2
            else:
                mixed_imaginary += (1j* self.croppedImages[1].imaginary)* ratio2

            if self.ui.comboBox_3.currentText()=="real":
                 mixed_real +=self.croppedImages[2].real * ratio3
            else:
                mixed_imaginary +=(1j* self.croppedImages[2].imaginary)* ratio3

            if self.ui.comboBox_4.currentText()=="real":
                 mixed_real +=self.croppedImages[3].real * ratio4
            else:
                mixed_imaginary+=(1j* self.croppedImages[3].imaginary)* ratio4
            
                
            avg_mixed_image = ( mixed_real + mixed_imaginary)
            # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
            final_mixed_image = np.fft.ifft2(avg_mixed_image)
          
            if (np.max(final_mixed_image)>1):
                final_mixed_image=final_mixed_image/np.max(final_mixed_image)
            plt.imsave('test2.png',np.abs(final_mixed_image) , cmap='gray')
            grayscale_image = QImage('test2.png').convertToFormat(QImage.Format_Grayscale8)
            
            self.output_window.addimage(self.output,grayscale_image)
            # grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8)



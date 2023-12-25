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
import time
from Worker import *

count = 0

Images=[]
Images1=[]
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
Qlabelsfixed=[]
filteredImages = Images.copy()
mode=""
class MyWindow(QMainWindow):
    work_requested = Signal(int)

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
        self.minHeight = 10000
        self.minWidth = 10000
        self.changed1.setIsCropable(True)
        for label in[self.fixed1, self.fixed2, self.fixed3, self.fixed4]:
            Qlabelsfixed.append(label)
        for fixed in [self.fixed1,self.fixed2,self.fixed3,self.fixed4]:
            fixed.setIsBrightness(True)
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
        self.ui.brightness_radio.setChecked(True)

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.progress.connect(self.UpdateProgressBar)
        self.worker.completed.connect(self.showOutput)
        self.work_requested.connect(self.worker.do_work)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.isInner = True
        self.overlay_color = QColor(255, 0, 0, 100)
        for combo in [self.ui.comboBox_1,self.ui.comboBox_2,self.ui.comboBox_3,self.ui.comboBox_4]:
            combo.addItems(["Magnitude","Phase","Real","Imaginary"])
        self.updatingComboBox(self.ui.comboBox_1,1)   
        self.ui.comboBox_1.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_1,1))
        self.ui.comboBox_2.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_2,2))
        self.ui.comboBox_3.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_3,3))
        self.ui.comboBox_4.currentTextChanged.connect(lambda: self.updatingComboBox(self.ui.comboBox_4,4))
        for slider in [self.ui.horizontalSlider,self.ui.horizontalSlider_2,self.ui.horizontalSlider_3,self.horizontalSlider_4]:
            slider.valueChanged.connect(self.UpdateLabels)
        self.UpdateLabels()
        # self.ui.widget.mousePressEvent  = lambda event: self.removeImage(1,self.fixed1,self.changed1)
        # self.ui.widget_2.mousePressEvent  = lambda event: self.removeImage(2,self.fixed2,self.changed2)
        # self.ui.widget_3.mousePressEvent  = lambda event: self.removeImage(3,self.fixed3,self.changed3)
        # self.ui.widget_4.mousePressEvent  = lambda event: self.removeImage(4,self.fixed4,self.changed4)
        #self.fixed1.mousePressEvent = lambda event: self.mousePressEvent(self.ui.fixedImage1)

        self.fixed1.doubleClicked.connect(lambda event: self.imageDisplay(self.fixed1,self.changed1,self.ui.comboBox_1,1))
        self.fixed2.doubleClicked.connect(lambda event: self.imageDisplay(self.fixed2,self.changed2,self.ui.comboBox_2,2))
        self.fixed3.doubleClicked.connect(lambda event: self.imageDisplay(self.fixed3,self.changed3,self.ui.comboBox_3,3))
        self.fixed4.doubleClicked.connect(lambda event: self.imageDisplay(self.fixed4,self.changed4,self.ui.comboBox_4,4))
        self.output_window.ui.pushButton.clicked.connect(self.Cancel)

        self.fixed1.BCchanged.connect(lambda: self.UpdateBC(self.fixed1,1,self.ui.comboBox_1))
        self.fixed2.BCchanged.connect(lambda: self.UpdateBC(self.fixed2,2,self.ui.comboBox_2))
        self.fixed3.BCchanged.connect(lambda: self.UpdateBC(self.fixed3,3,self.ui.comboBox_3))
        self.fixed4.BCchanged.connect(lambda: self.UpdateBC(self.fixed4,4,self.ui.comboBox_4))

        # for slider in [self.ui.horizontalSlider,self.ui.horizontalSlider_2,self.ui.horizontalSlider_3,self.ui.horizontalSlider_4]:
        #      slider.valueChanged.connect(lambda value, mode=mode: self.mixing(value))
        self.radioButton.toggled.connect(self.whichoutput)
        self.radioButton_2.toggled.connect(self.whichoutput)
        self.Inner_radio.toggled.connect(self.PhotoAdjustment)
        self.Outer_radio.toggled.connect(self.PhotoAdjustment)
        self.contrast_radio.toggled.connect(self.PhotoAdjustment)
        self.brightness_radio.toggled.connect(self.PhotoAdjustment)
        self.changed1.RubberBandChanged.connect(self.UpdateRubberBands)


        self.output = 1
        self.BC = None



    def open_output_window(self):
        global count
        # Create a new instance of the output window
            # Show the output window
        self.output_window.ui.progressBar.setValue(0)
        self.output_window.show()
        count = 1 
        self.worker.end = False
        self.mixing()

    def UpdateBC(self,Qlabel,imglabel,combobox):
        pass

    def UpdateRubberBands(self):
        Rect = self.changed1.Rect
        self.changed2.showRubberBand(Rect)
        self.changed3.showRubberBand(Rect)
        self.changed4.showRubberBand(Rect)
        

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

    def UpdateLabels(self):
        self.ui.label_6.setText(str(self.ui.horizontalSlider.value()))
        self.ui.label_7.setText(str(self.ui.horizontalSlider_2.value()))
        self.ui.label_8.setText(str(self.ui.horizontalSlider_3.value()))
        self.ui.label_9.setText(str(self.ui.horizontalSlider_4.value()))

    def imageInitializer(self,path,imglabel):
        img = Image()
        img.imagelabel=imglabel
        img.path = path
        # self.path
        # self.label = self.findChild(Qlabel, "Qlabel")
        img.original_image = QImage(img.path)
        grayscale_image = img.original_image.convertToFormat(QImage.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(grayscale_image)
        img.pixmap = self.pixmap
        img.grayscale = grayscale_image

        raw_data = plt.imread(img.path)
        raw_data = raw_data.astype('float32')
        raw_data /= 255
        img.raw_data=raw_data
        # Get size
        img.shape = img.raw_data.shape
        img.width = img.shape[1]
        img.height = img.shape[0]
        
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
        # global minHeigh, minWidth
        # if img.height < minHeigh:
        #     minHeigh = img.height
        # if img.width < minWidth:
        #     minWidth = img.width
        # for image in Images:
        #     if image.type != 0:
        #        if image.width > minWidth:
        #             image.width = minWidth
                    
        #        elif image.height > minHeigh:
        #             image.height = minHeigh
        return img,self.pixmap,grayscale_image
            
    def QImgtoImage(self,QImg,imglabel):
            QImg.save('temp.jpg')
            img, pixmap, grayscale_image = self.imageInitializer('temp.jpg',imglabel)
            os.remove('temp.jpg')
            return img
            #the Image returned doesn't have a path, don't try to access it

    def ResizeImgs(self):
        for image,label in zip(Images,Qlabelsfixed):
            if image.type!=0:
                pixmap=image.pixmap.scaled(self.minWidth, self.minHeight)
                label.setImage(pixmap,image,image.grayscale)
                original = QPixmap.fromImage(image.original_image).scaled(self.minWidth, self.minHeight)
                Qimg = original.toImage()
                newimg = self.QImgtoImage(Qimg,image.imagelabel)
                Images[image.imagelabel-1] = newimg
                

    def imageDisplay(self,Qlabel,Qlabel2,QComboBox,imglabel):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        path = filename[0]
        img,self.pixmap,grayscale_image = self.imageInitializer(path,imglabel)
        if img.height < self.minHeight:
            self.minHeight = img.height
            img.height=self.minHeight 
        if img.width < self.minWidth:
            self.minWidth = img.width
            img.width=self.minWidth
        Images[img.imagelabel-1] = img
        if Images[1].type!=0:
            # for i, label in enumerate(Qlabelsfixed)
            #     for ii,image in enumerate(Images):
            #      if image.type!=0:
            #         if ii==i:
            #             pixmap=image.pixmap.scaled(self.minWidth, self.minHeight)
            #             Qimg = pixmap.toImage()
            #             newimg = self.QImgtoImage(Qimg,img.imagelabel)
            #             Images[img.imagelabel-1] = newimg
            #             label.setImage(pixmap,image,image.grayscale)
            self.ResizeImgs()
                        

        # if self.minHeight!=10000 and self.minWidth!=10000:
        #     self.pixmap = self.pixmap.scaled(self.minWidth, self.minHeight, QtCore.Qt.KeepAspectRatio)
        else:
           Qlabel.setImage(img.pixmap,img,grayscale_image)

        # Images[img.imagelabel-1] = img
        self.updatingComboBox(self.ui.comboBox_1,1)
        self.updatingComboBox(self.ui.comboBox_2,2)
        self.updatingComboBox(self.ui.comboBox_3,3)
        self.updatingComboBox(self.ui.comboBox_4,4)
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
    
    def PhotoAdjustment(self):
        if self.Inner_radio.isChecked():
            self.isInner = True
            self.changed1.setIsCropable(True)
        elif self.Outer_radio.isChecked():
            self.isInner = False
            self.changed1.setIsCropable(True)
        if self.brightness_radio.isChecked():
            for fixed in [self.fixed1,self.fixed2,self.fixed3,self.fixed4]:
                fixed.setIsBrightness(True)
        elif self.contrast_radio.isChecked():
            for fixed in [self.fixed1,self.fixed2,self.fixed3,self.fixed4]:
                fixed.setIsContrast(True)
            
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
        Qlabel.setImage(QPixmap(grayscale_image).scaled(self.minWidth,self.minHeight),img,grayscale_image) #changed line

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
        if Rect == QRect(QPoint(0,0),QtCore.QSize()):
            pass
        elif self.isInner == True or self.isInner == False:
            if Images[0].type!=0:
                self.fixed1.getCropped(Rect)
                img,pixmap,grayscale_image = self.imageInitializer('output1.jpg',1)
                self.croppedImages[0]=img
            if Images[1].type!=0:
                self.fixed2.getCropped(Rect)
                img,pixmap,grayscale_image = self.imageInitializer('output2.jpg',2)
                self.croppedImages[1]=img
            if Images[2].type!=0:
                self.fixed3.getCropped(Rect)
                img,pixmap,grayscale_image = self.imageInitializer('output3.jpg',3)
                self.croppedImages[2]=img
            if Images[3].type!=0:
                self.fixed4.getCropped(Rect)
                img,pixmap,grayscale_image = self.imageInitializer('output4.jpg',4)
                self.croppedImages[3]=img
        elif self.isInner == False:
            if Images[0].type!=0:
                self.croppedImages[0].raw_data = Images[0].raw_data - self.croppedImages[0].raw_data
                self.croppedImages[0].fft = np.fft.fft2(self.croppedImages[0].raw_data)
                self.croppedImages[0].magnitude = np.abs(self.croppedImages[0].fft)
                self.croppedImages[0].phase = np.angle(self.croppedImages[0].fft)
                self.croppedImages[0].real = np.real(self.croppedImages[0].fft)
                self.croppedImages[0].imaginary = np.imag(self.croppedImages[0].fft)    
            if Images[1].type!=0:
                self.croppedImages[1].raw_data = Images[1].raw_data - self.croppedImages[1].raw_data
                self.croppedImages[1].fft = np.fft.fft2(self.croppedImages[1].raw_data)
                self.croppedImages[1].magnitude = np.abs(self.croppedImages[1].fft)
                self.croppedImages[1].phase = np.angle(self.croppedImages[1].fft)
                self.croppedImages[1].real = np.real(self.croppedImages[1].fft)
                self.croppedImages[1].imaginary = np.imag(self.croppedImages[1].fft)    
            if Images[2].type!=0:
                self.croppedImages[2].raw_data = Images[2].raw_data - self.croppedImages[2].raw_data
                self.croppedImages[2].fft = np.fft.fft2(self.croppedImages[2].raw_data)
                self.croppedImages[2].magnitude = np.abs(self.croppedImages[2].fft)
                self.croppedImages[2].phase = np.angle(self.croppedImages[2].fft)
                self.croppedImages[2].real = np.real(self.croppedImages[2].fft)
                self.croppedImages[2].imaginary = np.imag(self.croppedImages[2].fft)    
            if Images[3].type!=0:
                self.croppedImages[3].raw_data = Images[3].raw_data - self.croppedImages[3].raw_data
                self.croppedImages[3].fft = np.fft.fft2(self.croppedImages[3].raw_data)
                self.croppedImages[3].magnitude = np.abs(self.croppedImages[3].fft)
                self.croppedImages[3].phase = np.angle(self.croppedImages[3].fft)
                self.croppedImages[3].real = np.real(self.croppedImages[3].fft)
                self.croppedImages[3].imaginary = np.imag(self.croppedImages[3].fft)    

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
                self.tempImg = grayscale_image            
                        
            elif(mode=='real-imag'):
                
                mixed_imaginary= np.zeros_like(self.croppedImages[0].imaginary,dtype=np.complex128)
                mixed_real = np.ones_like(self.croppedImages[0].real)
                if self.ui.comboBox_1.currentText()=="Real":
                    mixed_real =self.croppedImages[0].real * ratio1
                else:
                    mixed_imaginary =(1j* self.croppedImages[0].imaginary)* ratio1

                if  self.ui.comboBox_2.currentText()=="Real":
                    mixed_real +=self.croppedImages[1].real * ratio2
                else:
                    mixed_imaginary += (1j* self.croppedImages[1].imaginary)* ratio2

                if self.ui.comboBox_3.currentText()=="Real":
                    mixed_real +=self.croppedImages[2].real * ratio3
                else:
                    mixed_imaginary +=(1j* self.croppedImages[2].imaginary)* ratio3


                if self.ui.comboBox_4.currentText()=="Real":
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
                self.tempImg = grayscale_image
                # grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8)
        self.Progressing(5)

    def Progressing(self,value):
        self.output_window.ui.progressBar.setMaximum(value)
        self.work_requested.emit(value)

    def Cancel(self):
        self.worker.end = True

    def showOutput(self):
        self.output_window.addimage(self.output,self.tempImg)

    def UpdateProgressBar(self,value):
        self.output_window.ui.progressBar.setValue(value)
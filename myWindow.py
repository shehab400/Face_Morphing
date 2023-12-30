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
from scipy.fft import fft2 , fftshift
import copy

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
fftcopy=[]
filteredImages = [None,None,None,None]
mode=""
class MyWindow(QMainWindow):
    work_requested = Signal(int)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("GUI.ui", self)
        self.setWindowTitle('Fourier Transform Mixer')
        self.croppedImages = [None,None,None,None]
        self.fixed1 = QExampleLabel(self,1)
        self.fixed2 = QExampleLabel(self,2)
        self.fixed3 = QExampleLabel(self,3)
        self.fixed4 = QExampleLabel(self,4)
        self.changed1 = QExampleLabel(self,1)
        self.changed2 = QExampleLabel(self,2)
        self.changed3 = QExampleLabel(self,3)
        self.changed4 = QExampleLabel(self,4)
        self.fixed1.setAlignment(QtCore.Qt.AlignCenter)
        self.fixed2.setAlignment(QtCore.Qt.AlignCenter)
        self.fixed3.setAlignment(QtCore.Qt.AlignCenter)
        self.fixed4.setAlignment(QtCore.Qt.AlignCenter)
        self.changed1.setAlignment(QtCore.Qt.AlignCenter)
        self.changed2.setAlignment(QtCore.Qt.AlignCenter)
        self.changed3.setAlignment(QtCore.Qt.AlignCenter)
        self.changed4.setAlignment(QtCore.Qt.AlignCenter)
        self.minHeight = 10000
        self.minWidth = 10000
        self.changed1.setIsCropable(True)
        for label in[self.fixed1, self.fixed2, self.fixed3, self.fixed4]:
            Qlabelsfixed.append(label)
        for fixed in [self.fixed1,self.fixed2,self.fixed3,self.fixed4]:
            fixed.setIsBrightness(True)
        # self.output_window = OutputWindow()
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
        # self.output_window.ui.pushButton.clicked.connect(self.Cancel)

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
        self.ui.progressBar.setValue(0)
        # self.output_window.ui.progressBar.setValue(0)
        # self.output_window.show()
        count = 1 
        self.worker.end = False
        self.mixing()
        
    def addImageInMain(self,key,QImage):
        if key == 1:
            self.ui.output_1.clear()
            self.ui.output_1.setPixmap(QPixmap(QImage))
        elif key == 2:
            self.ui.output_2.clear()
            self.ui.output_2.setPixmap(QPixmap(QImage))

    def UpdateBC(self,Qlabel,imglabel,combobox):
        img = self.QImgtoImage(Qlabel.Qimg,imglabel)
        Images[imglabel-1] = img
        self.updatingComboBox(combobox,imglabel)
        for i,img in zip(range(len(Images)),Images):
            self.croppedImages[i] = img.copy()

    def UpdateRubberBands(self):
        Rect = self.changed1.Rect
        for i,changed in zip([1,2,3],[self.changed2,self.changed3,self.changed4]):
            if Images[i].type!=0:
                changed.showRubberBand(Rect)
        

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
        img.raw_data = np.mean(raw_data, axis=-1)
        # Get size
        img.shape = img.raw_data.shape
        img.width = img.shape[1]
        img.height = img.shape[0]

        img.freqx = np.fft.fftfreq(img.shape[0])
        img.freqy = np.fft.fftfreq(img.shape[1])
        
        # # Fourier FFT
        img.fft = np.fft.fft2(img.raw_data)
        img.fft=np.fft.fftshift(img.fft)
       
        print(img.fft.shape)
        
        # # Get magnitude
        # img.magnitude = np.abs(img.fft)
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
                label.Qimg = Qimg
                newimg = self.QImgtoImage(Qimg,image.imagelabel)
                Images[image.imagelabel-1] = newimg
                

    def imageDisplay(self,Qlabel,Qlabel2,QComboBox,imglabel):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        path = filename[0]
        Qlabel.setOriginalPath(path)
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
            fftcopy.append(img.fft)
                        

        # if self.minHeight!=10000 and self.minWidth!=10000:
        #     self.pixmap = self.pixmap.scaled(self.minWidth, self.minHeight, QtCore.Qt.KeepAspectRatio)
        else:
           Qlabel.setImage(img.pixmap,img,grayscale_image)
           fftcopy.append(img.fft)

        # Images[img.imagelabel-1] = img
        self.updatingComboBox(self.ui.comboBox_1,1)
        self.updatingComboBox(self.ui.comboBox_2,2)
        self.updatingComboBox(self.ui.comboBox_3,3)
        self.updatingComboBox(self.ui.comboBox_4,4)
        print(img.imagelabel)

        # print(len(Images)) # need to create remove image function to update length of images array
        for i,img in zip(range(len(Images)),Images):
            self.croppedImages[i] = img.copy()
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
            grayscale_image = QImage('test.png')
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Real"] :
            real_part_normalized = (img.real - np.min(img.real)) / (np.max(img.real) - np.min(img.real))
            plt.imsave('test.png',real_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png')
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Phase"] :
            phase_part_normalized = (img.phase - np.min(img.phase)) / (np.max(img.phase) - np.min(img.phase))
            plt.imsave('test.png',phase_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png')
            filteredImages[img.imagelabel-1] = grayscale_image
        if component in ["Imaginary"] :
            imaginary_part_normalized = (img.imaginary - np.min(img.imaginary)) / (np.max(img.imaginary) - np.min(img.imaginary))
            plt.imsave('test.png',imaginary_part_normalized , cmap='gray')
            grayscale_image = QImage('test.png')
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
        # self.croppedImages = Images.copy()
        # for fft, img in zip(fftcopy,self.croppedImages):
        #     img.fft=fft
        for cropped,img in zip(self.croppedImages,Images):
            cropped = img.copy()
        self.crop = Rect
        # if os.path.exists('temp.jpg'):
        #     os.remove('temp.jpg')
        # if os.path.exists('zeros.jpg'):
        #     os.remove('zeros.jpg')
        temparray = [Image(),Image(),Image(),Image()]
        if Rect == None or Rect == QRect(self.changed1.originQPoint,QtCore.QSize()):
            for i,img in zip(range(len(Images)),Images):
                temparray[i] = img.copy()
        elif self.isInner == True:
            # for i,image,fixed in zip([1,2,3,4],Images,Qlabelsfixed):
            #     if image.type!=0:
            #         fixed.getCropped(Rect)
            #         img,pixmap,grayscale_image = self.imageInitializer('output'+str(i)+'.jpg',i)
            #         self.croppedImages[i-1] = img
            ratio = self.changed1.getRatio()*1.5
            for i in range(4):
                # maxfreqx = ratio * np.max(self.croppedImages[i].freqx)
                # maxfreqy = ratio * np.max(self.croppedImages[i].freqy)
                # indicesx = np.where((self.croppedImages[i].freqx >= maxfreqx) + (self.croppedImages[i].freqx <= -maxfreqx))
                # indicesy = np.where((self.croppedImages[i].freqy >= maxfreqy) + (self.croppedImages[i].freqy <= -maxfreqy))
                
                # indicesx = list(indicesx[0])
                # indicesy = list(indicesy[0])
                # print(len(indicesx))
                # print(len(indicesy))
                # # newfft = []
                # # for j in range(len(indicesx)):
                # #     newfft.append([])
                # for ii in indicesx:
                #     for iii in indicesy:
                #         self.croppedImages[i].fft[ii][iii] = 0
                # print(self.croppedImages[i].fft[indicesx[1]][indicesy[1]])
                
                temparray[i].fft = self.apply_low_pass_filter(self.croppedImages[i],ratio)
                temparray[i].magnitude = np.abs(temparray[i].fft)
                temparray[i].phase = np.angle(temparray[i].fft)
                temparray[i].real = np.real(temparray[i].fft)
                temparray[i].imaginary = np.imag(temparray[i].fft)
            # self.croppedImages[0].freqx = newfreqx
            # self.croppedImages[0].freqy = newfreqy
            # print(newfreqx)
            # print(newfreqy)
            # for i in range(len(self.croppedImages[0].fft)):
            #     for ii in range(len(self.croppedImages[0].fft[0])):
            #         for iii in range(len(self.croppedImages[0].fft[i][ii])):


            # if Images[0].type!=0:
            #     self.fixed1.getCropped(Rect)
            #     img,pixmap,grayscale_image = self.imageInitializer('output1.jpg',1)
            #     self.croppedImages[0]=img
            # if Images[1].type!=0:
            #     self.fixed2.getCropped(Rect)
            #     img,pixmap,grayscale_image = self.imageInitializer('output2.jpg',2)
            #     self.croppedImages[1]=img
            # if Images[2].type!=0:
            #     self.fixed3.getCropped(Rect)
            #     img,pixmap,grayscale_image = self.imageInitializer('output3.jpg',3)
            #     self.croppedImages[2]=img
            # if Images[3].type!=0:
            #     self.fixed4.getCropped(Rect)
            #     img,pixmap,grayscale_image = self.imageInitializer('output4.jpg',4)
            #     self.croppedImages[3]=img
        elif self.isInner == False:
            ratio = self.changed1.getRatio()
            for i in range(4):
                # maxfreqx = 0.5 * np.max(self.croppedImages[i].freqx)
                # maxfreqy = 0.5 * np.max(self.croppedImages[i].freqy)
                # indicesx = np.where((self.croppedImages[i].freqx <= maxfreqx) * (self.croppedImages[i].freqx >= -maxfreqx))
                # indicesy = np.where((self.croppedImages[i].freqy <= maxfreqy) * (self.croppedImages[i].freqy >= -maxfreqy))
                # indicesx = list(indicesx[0])
                # indicesy = list(indicesy[0])
                # print(len(indicesx))
                # print(len(indicesy))
                # newfft = []
                # for j in range(len(indicesx)):
                #     newfft.append([])
                # c=-1
                # for ii in indicesx:
                #     c+=1
                #     for iii in indicesy:
                #         newfft[c].append(self.croppedImages[i].fft[ii][iii])
                
                # for x, y in zip(indicesx, indicesy):
                #   self.croppedImages[i].fft[x, y] = 0
               
                # self.croppedImages[i].fft = newfft
                temparray[i].fft = self.apply_high_pass_filter(self.croppedImages[i],ratio)
                temparray[i].magnitude = np.abs(temparray[i].fft)
                temparray[i].phase = np.angle(temparray[i].fft)
                temparray[i].real = np.real(temparray[i].fft)
                temparray[i].imaginary = np.imag(temparray[i].fft)
            # for image,cropped in zip(Images,self.croppedImages):
            #     if image.type!=0:
            #         cropped.raw_data = image.raw_data - cropped.raw_data
            #         cropped.fft = np.fft.fft2(cropped.raw_data)
            #         cropped.magnitude = np.abs(cropped.fft)
            #         cropped.phase = np.angle(cropped.fft)
            #         cropped.real = np.real(cropped.fft)
            #         cropped.imaginary = np.imag(cropped.fft)

            # if Images[0].type!=0:
            #     self.croppedImages[0].raw_data = Images[0].raw_data - self.croppedImages[0].raw_data
            #     self.croppedImages[0].fft = np.fft.fft2(self.croppedImages[0].raw_data)
            #     self.croppedImages[0].magnitude = np.abs(self.croppedImages[0].fft)
            #     self.croppedImages[0].phase = np.angle(self.croppedImages[0].fft)
            #     self.croppedImages[0].real = np.real(self.croppedImages[0].fft)
            #     self.croppedImages[0].imaginary = np.imag(self.croppedImages[0].fft)    
            # if Images[1].type!=0:
            #     self.croppedImages[1].raw_data = Images[1].raw_data - self.croppedImages[1].raw_data
            #     self.croppedImages[1].fft = np.fft.fft2(self.croppedImages[1].raw_data)
            #     self.croppedImages[1].magnitude = np.abs(self.croppedImages[1].fft)
            #     self.croppedImages[1].phase = np.angle(self.croppedImages[1].fft)
            #     self.croppedImages[1].real = np.real(self.croppedImages[1].fft)
            #     self.croppedImages[1].imaginary = np.imag(self.croppedImages[1].fft)    
            # if Images[2].type!=0:
            #     self.croppedImages[2].raw_data = Images[2].raw_data - self.croppedImages[2].raw_data
            #     self.croppedImages[2].fft = np.fft.fft2(self.croppedImages[2].raw_data)
            #     self.croppedImages[2].magnitude = np.abs(self.croppedImages[2].fft)
            #     self.croppedImages[2].phase = np.angle(self.croppedImages[2].fft)
            #     self.croppedImages[2].real = np.real(self.croppedImages[2].fft)
            #     self.croppedImages[2].imaginary = np.imag(self.croppedImages[2].fft)    
            # if Images[3].type!=0:
            #     self.croppedImages[3].raw_data = Images[3].raw_data - self.croppedImages[3].raw_data
            #     self.croppedImages[3].fft = np.fft.fft2(self.croppedImages[3].raw_data)
            #     self.croppedImages[3].magnitude = np.abs(self.croppedImages[3].fft)
            #     self.croppedImages[3].phase = np.angle(self.croppedImages[3].fft)
            #     self.croppedImages[3].real = np.real(self.croppedImages[3].fft)
            #     self.croppedImages[3].imaginary = np.imag(self.croppedImages[3].fft)    

            # self.croppedImages = Images.copy()
            # self.fixed1.zeros.save('zeros.jpg')
            # img = QImage('zeros.jpg')
            # os.remove('zeros.jpg')
            # cropped = self.fixed1.cropImg(img,Rect)
            # cropped.save('zeros.jpg')
            # self.zeros = PIL.Image.open('zeros.jpg')

        self.setMode()
        global mode
        print(mode)
        if all(img.type != 0 for img in Images):
            # firstcomponent=self.chooseComponent(type1,ratio1,Images[0])
            # secoundcomponent=self.chooseComponent(type2,ratio2,Images[1])
            # thirdcomponent=self.chooseComponent(type3,ratio3,Images[2])
            # fourthcomponent=self.chooseComponent(type4,ratio4,Images[3])
            if(mode=='mag-phase'):
            
                mixed_magnitude = np.zeros_like(temparray[0].magnitude,np.float64)
                mixed_phase = np.zeros_like(temparray[0].phase,dtype=np.complex128)
                if self.ui.comboBox_1.currentText()=="Magnitude":
                    mixed_magnitude =temparray[0].magnitude * ratio1
                else:
                    mixed_phase = np.exp(1j * temparray[0].phase)* ratio1

                if  self.ui.comboBox_2.currentText()=="Magnitude":
                    mixed_magnitude +=temparray[1].magnitude * ratio2
                else:
                    # if np.max(np.angle(mixed_phase)) == 0:
                    #     mixed_phase = np.exp(1j * temparray[1].phase)* ratio2
                    # else:
                        mixed_phase += np.exp(1j * temparray[1].phase)* ratio2

                if self.ui.comboBox_3.currentText()=="Magnitude":
                    mixed_magnitude +=temparray[2].magnitude * ratio3
                else:
                    # if np.max(np.angle(mixed_phase)) == 0:
                    #     mixed_phase =np.exp(1j * temparray[2].phase)*ratio3
                    # else:
                        mixed_phase +=np.exp(1j * temparray[2].phase)*ratio3

                if self.ui.comboBox_4.currentText()=="Magnitude":
                    mixed_magnitude +=temparray[3].magnitude * ratio4
                else:
                    # if np.max(np.angle(mixed_phase)) == 0:
                    #     mixed_phase = np.exp(1j * temparray[3].phase)* ratio4
                    # else:
                        mixed_phase+= np.exp(1j * temparray[3].phase)* ratio4


                if np.max(np.angle(mixed_phase)) == 0:
                    
                    avg_mixed_image = np.fft.ifftshift(mixed_magnitude)
                    
                    # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                    final_mixed_image = np.fft.ifft2(avg_mixed_image)
                elif(np.max(mixed_magnitude==0)):
                    avg_mixed_image = np.fft.ifftshift(mixed_phase)
                    # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                    final_mixed_image = np.fft.ifft2(avg_mixed_image)
                else:
                    avg_mixed_image = np.fft.ifftshift(mixed_magnitude *  mixed_phase)
                    # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                    final_mixed_image = np.fft.ifft2(avg_mixed_image)
                if (np.max(final_mixed_image)>1):
                    final_mixed_image=final_mixed_image/np.max(final_mixed_image)
                plt.imsave('test1.png',np.abs(final_mixed_image) ,cmap='gray')
                self.tempImg = QImage('test1.png')         
                        
            elif(mode=='real-imag'):
                
                mixed_imaginary= np.zeros_like(temparray[0].imaginary,dtype=np.complex128)
                mixed_real = np.zeros_like(temparray[0].real)
                if self.ui.comboBox_1.currentText()=="Real":
                    mixed_real =temparray[0].real * ratio1
                else:
                    mixed_imaginary =(1j* temparray[0].imaginary)* ratio1

                if  self.ui.comboBox_2.currentText()=="Real":
                    mixed_real +=temparray[1].real * ratio2
                else:
                    # if np.max(np.angle(mixed_imaginary)) == 0:
                    #    mixed_imaginary = (1j* temparray[1].imaginary)* ratio2 
                    # else:   
                       mixed_imaginary += (1j* temparray[1].imaginary)* ratio2

                if self.ui.comboBox_3.currentText()=="Real":
                    mixed_real +=temparray[2].real * ratio3 
                else:
                    # if np.max(np.angle(mixed_imaginary)) == 0:
                    #     mixed_imaginary =(1j* temparray[2].imaginary)* ratio3
                    # else:
                        mixed_imaginary +=(1j* temparray[2].imaginary)* ratio3


                if self.ui.comboBox_4.currentText()=="Real":
                    mixed_real +=temparray[3].real * ratio4
                else:
                    # if np.max(np.angle(mixed_imaginary)) == 0:
                    #     mixed_imaginary = (1j* temparray[3].imaginary)* ratio4
                    # else:
                        mixed_imaginary+=(1j* temparray[3].imaginary)* ratio4
                
                    
                avg_mixed_image = np.fft.ifftshift( mixed_real + mixed_imaginary)
                # normalized=(avg_mixed_image-np.min(avg_mixed_image))/(np.max(avg_mixed_image)-np.min(avg_mixed_image))
                final_mixed_image = np.fft.ifft2(avg_mixed_image)
            
                if (np.max(final_mixed_image)>1):
                    final_mixed_image=final_mixed_image/np.max(final_mixed_image)
                plt.imsave('test2.png',np.abs(final_mixed_image) , cmap='gray')
                self.tempImg = QImage('test2.png')
                # grayscale_image = QImage('test1.png').convertToFormat(QImage.Format_Grayscale8)
        self.Progressing(4)

    def Progressing(self,value):
        self.ui.progressBar.setMaximum(value)
        # self.output_window.ui.progressBar.setMaximum(value)
        self.work_requested.emit(value)

    def Cancel(self):
        self.worker.end = True

    def showOutput(self):
        if self.crop != QRect(QPoint(0,0),QtCore.QSize()) and self.isInner == False:
            self.tempImg.save('temp.jpg')
            # img = PIL.Image.open('temp.jpg')
            # img.paste(self.zeros,(self.crop.x(),self.crop.y()))
            # img.save('temp.jpg')
            self.tempImg = QImage('temp.jpg')
        self.addImageInMain(self.output,self.tempImg)
        # self.output_window.addimage(self.output,self.tempImg)

    def UpdateProgressBar(self,value):
        self.ui.progressBar.setValue(value)
        # self.output_window.ui.progressBar.setValue(value)
        
    def apply_high_pass_filter(self, image, ratio):
        fft_shifted = image.fft
        freqx = image.freqx
        freqy = image.freqy
        maxfreqx = ratio * np.max(freqx)
        maxfreqy = ratio * np.max(freqy)
        high_pass_filter = np.ones_like(fft_shifted)
        high_pass_filter[np.abs(freqx) <= maxfreqx, :] = 0
        high_pass_filter[:, np.abs(freqy) <= maxfreqy] = 0
        filtered_fft = fft_shifted * high_pass_filter
        return filtered_fft
        # filtered_image = np.abs(np.fft.ifft2(np.fft.ifftshift(filtered_fft)))
        
    def apply_low_pass_filter(self, image, ratio):
        fft_shifted = image.fft
        freqx = image.freqx
        freqy = image.freqy
        maxfreqx = ratio * np.max(freqx)
        maxfreqy = ratio * np.max(freqy)
        low_pass_filter = np.zeros_like(fft_shifted)
        low_pass_filter[np.abs(freqx) <= maxfreqx, :] = 1
        low_pass_filter[:, np.abs(freqy) <= maxfreqy] = 1
        filtered_fft = fft_shifted * low_pass_filter
        # filtered_image = np.abs(np.fft.ifft2(np.fft.ifftshift(filtered_fft)))
        return filtered_fft
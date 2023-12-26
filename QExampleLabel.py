import sys
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import QRect,QPoint,pyqtSignal,pyqtSlot
import cv2
import numpy as np
import os

class QExampleLabel (QLabel):
    BCchanged = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    RubberBandChanged = pyqtSignal(int)
    @pyqtSlot(int)

    def __init__(self, parentQWidget = None,flag = 0):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.Label = QLabel
        self.isCropable = False
        self.currentQRubberBand = None
        self.croppedPixmap = None
        self.img = None
        self.Qimg = None
        self.originalQimg = None
        self.grayscale_image = None
        self.flag = flag
        self.isContrast = False
        self.isBrightness = False
        self.contrast = 1
        self.brightness = 0
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def setImage (self,pixmap,img,grayscale_image):
        self.img = img
        self.Qimg = QImage(img.path)
        self.originalQimg = QImage(img.path)
        self.grayscale_image = grayscale_image
        self.setPixmap(pixmap)
        self.croppedPixmap = pixmap

    def removeImage(self):
        QLabel.clear()

    def setIsCropable(self,bool):
        self.isCropable = bool
        if bool == True:
            self.isContrast = False
            self.isBrightness = False

    def setIsBrightness(self,bool):
        self.isBrightness = bool
        if bool == True:
            self.isCropable = False
            self.isContrast = False

    def setIsContrast(self,bool):
        self.isContrast = bool
        if bool == True:
            self.isCropable = False
            self.isBrightness = False

    def resetRubberBand(self):
        if self.currentQRubberBand != None:
            self.currentQRubberBand.hide()
        self.currentQRubberBand = None
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def mouseDoubleClickEvent(self, evenQMouseEvent):
        self.doubleClicked.emit(1)

    def mousePressEvent (self, eventQMouseEvent):
        self.SecondQPoint = None
        if self.isCropable == True:
            if self.currentQRubberBand != None:
                self.currentQRubberBand.hide()
            self.originQPoint = eventQMouseEvent.pos()
            self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QtCore.QSize()))
            self.currentQRubberBand.show()
        elif self.isBrightness == True or self.isContrast == True:
            self.originQPoint = eventQMouseEvent.pos()

    def mouseMoveEvent (self, eventQMouseEvent):
        if self.isCropable == True:
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())
        elif self.isBrightness == True or self.isContrast == True:
            self.SecondQPoint = eventQMouseEvent.pos()
            if self.isBrightness == True:
                self.brightness = self.originQPoint.y() - self.SecondQPoint.y()
                self.changeBC()
            elif self.isContrast == True:
                self.contrast = self.SecondQPoint.x() - self.originQPoint.x()
                self.changeBC()


    def mouseReleaseEvent (self, eventQMouseEvent):
        if self.SecondQPoint == None:
            self.SecondQPoint = self.originQPoint
        if self.isCropable == True:
            currentQRect = self.currentQRubberBand.geometry()
            self.Rect = currentQRect
            self.RubberBandChanged.emit(1)
            cropQPixmap = self.pixmap().copy(currentQRect)
            self.croppedPixmap = cropQPixmap
        elif self.isBrightness == True:
            self.brightness = self.originQPoint.y() - self.SecondQPoint.y()
            self.changeBC()
        elif self.isContrast == True:
            self.contrast = self.SecondQPoint.x() - self.originQPoint.x()
            self.changeBC()

    def getCropped(self,QRect):
        Image = self.Qimg
        original = QPixmap.fromImage(Image)
        cropped = original.copy(QRect)
        cropped.save('output'+str(self.flag)+'.jpg')
        return cropped
    
    def showRubberBand(self,Rect):
        if self.currentQRubberBand != None:
            self.currentQRubberBand.hide()
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(Rect)
        self.currentQRubberBand.show()

    def changeBC(self):
        if self.contrast == 0:
            self.contrast = 1
        elif self.contrast > 1:
            self.contrast = self.contrast / 10
        elif self.contrast < 0:
            self.contrast = 10/abs(self.contrast)
        t = self.qimg2cv(self.grayscale_image)
        Image = cv2.addWeighted(t, self.contrast, t, 0, self.brightness)
        cv2.imwrite('temp.jpg',Image)
        img = QImage('temp.jpg')
        self.setPixmap(QPixmap.fromImage(img))
        if os.path.exists('temp.jpg'):
            os.remove('temp.jpg')
        t2 = self.qimg2cv(self.originalQimg)
        Image2 = cv2.addWeighted(t2, self.contrast, t2, 0, self.brightness)
        cv2.imwrite('temp.jpg',Image2)
        self.Qimg = QImage('temp.jpg')
        if os.path.exists('temp.jpg'):
            os.remove('temp.jpg')
        self.BCchanged.emit(1)

    def qimg2cv(self, q_img):
        q_img.save('temp.jpg', 'jpg')
        mat = cv2.imread('temp.jpg')
        if os.path.exists('temp.jpg'):
            os.remove("temp.jpg")
        return mat

if __name__ == '__main__':
    myQApplication = QApplication(sys.argv)
    myQExampleLabel = QExampleLabel()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
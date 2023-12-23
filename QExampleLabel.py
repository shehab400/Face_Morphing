import sys
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import QRect,QPoint
import cv2
import numpy as np

class QExampleLabel (QLabel):
    def __init__(self, parentQWidget = None,flag = 0):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.Label = QLabel
        self.isCropable = False
        self.currentQRubberBand = None
        self.croppedPixmap = None
        self.img = None
        self.flag = flag
        self.isContrast = False
        self.isBrightness = False
        self.contrast = 0
        self.brightness = 0
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def setImage (self,pixmap,img):
        self.img = img
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

    def mousePressEvent (self, eventQMouseEvent):
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

    def mouseReleaseEvent (self, eventQMouseEvent):
        if self.isCropable == True:
            currentQRect = self.currentQRubberBand.geometry()
            self.Rect = currentQRect
            cropQPixmap = self.pixmap().copy(currentQRect)
            self.croppedPixmap = cropQPixmap
        elif self.isBrightness == True:
            self.brightness = self.originQPoint.y() - self.SecondQPoint.y()
        elif self.isContrast == True:
            self.contrast = self.SecondQPoint.x() - self.originQPoint.x()

    def getCropped(self,QRect):
        Image = QImage(self.img.path)
        original = QPixmap.fromImage(Image)
        cropped = original.copy(QRect)
        cropped.save('output'+str(self.flag)+'.jpg')
        return cropped

    def changBC(self):
        Image = cv2.addWeighted(self.img, self.contrast, np.zeros(self.img.shape, self.img.dtype), self.brightness , 50)
        return Image

if __name__ == '__main__':
    myQApplication = QApplication(sys.argv)
    myQExampleLabel = QExampleLabel()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
import sys
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect,QPoint
import cv2
import numpy as np

class QExampleLabel (QLabel):
    def __init__(self, parentQWidget = None,flag = 0):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.isCropable = False
        self.currentQRubberBand = None
        self.croppedPixmap = None
        self.img = None
        self.flag = flag
        self.contrasted = 0
        self.brightned = 0
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def setImage (self,pixmap,img):
        self.img = img
        self.setPixmap(pixmap)
        self.croppedPixmap = pixmap

    def removeImage(self):
        QLabel.clear()

    def setIsCropable(self,bool):
        self.isCropable = bool

    def resetRubberBand(self):
        if self.currentQRubberBand != None:
            self.currentQRubberBand.hide()
        self.currentQRubberBand = None
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def mousePressEvent (self, eventQMouseEvent):
        if self.isCropable == False:
            return
        if self.currentQRubberBand != None:
            self.currentQRubberBand.hide()
        self.originQPoint = eventQMouseEvent.pos()
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent (self, eventQMouseEvent):
        if self.isCropable == False:
            return
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())

    def mouseReleaseEvent (self, eventQMouseEvent):
        if self.isCropable == False:
            return
        currentQRect = self.currentQRubberBand.geometry()
        self.Rect = currentQRect
        cropQPixmap = self.pixmap().copy(currentQRect)
        self.croppedPixmap = cropQPixmap
        #cropQPixmap.save('output.png')

    def getCropped(self,QRect):
        cropped = self.pixmap().copy(QRect)
        cropped.save('output'+str(self.flag)+'.png')
        return cropped

    def changBC(self):
        BCimage = cv2.addWeighted(self.img, self.contrasted, np.zeros(self.img.shape, self.img.dtype), self.brightned , 50)


if __name__ == '__main__':
    myQApplication = QApplication(sys.argv)
    myQExampleLabel = QExampleLabel()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
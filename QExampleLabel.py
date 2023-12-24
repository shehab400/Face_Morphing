import sys
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QMouseEvent, QPixmap,QImage
from PyQt5.QtCore import QRect,QPoint,pyqtSignal,pyqtSlot
import cv2
import os

class QExampleLabel (QLabel):
    brightnessChanged = pyqtSignal(int)
    contrastChanged = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    @pyqtSlot(int)

    def __init__(self, parentQWidget = None,flag = 0):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.Label = QLabel
        self.isCropable = False
        self.currentQRubberBand = None
        self.croppedPixmap = None
        self.img = None
        self.Qimg = None
        self.grayscale_image = None
        self.flag = flag
        self.isContrast = False
        self.isBrightness = False
        self.contrast = 0
        self.brightness = 0
        self.Rect = QRect(QPoint(0,0),QtCore.QSize())

    def setImage (self,pixmap,img,grayscale_image):
        self.img = img
        self.Qimg = QImage(self.img.path)
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
                self.changeB()
            elif self.isContrast == True:
                self.contrast = self.SecondQPoint.x() - self.originQPoint.x()
                self.ChangeC()

    def mouseReleaseEvent (self, eventQMouseEvent):
        if self.isCropable == True:
            currentQRect = self.currentQRubberBand.geometry()
            self.Rect = currentQRect
            cropQPixmap = self.pixmap().copy(currentQRect)
            self.croppedPixmap = cropQPixmap
        elif self.isBrightness == True:
            if self.SecondQPoint == None:
                self.SecondQPoint = self.originQPoint
            self.brightness = self.originQPoint.y() - self.SecondQPoint.y()
            self.changeB()
        elif self.isContrast == True:
            if self.SecondQPoint == None:
                self.SecondQPoint = self.originQPoint
            self.contrast = self.SecondQPoint.x() - self.originQPoint.x()
            self.ChangeC()

    def getCropped(self,QRect):
        original = QPixmap.fromImage(self.Qimg)
        cropped = original.copy(QRect)
        cropped.save('output'+str(self.flag)+'.jpg')
        return cropped

    def changeB(self):
        src1 = self.qimg2cv(self.grayscale_image)
        Image = self.change_brightness(src1,self.brightness)
        cv2.imwrite("image_processed.jpg", Image)
        self.setPixmap(QPixmap.fromImage(QImage('image_processed.jpg')))
        if os.path.exists('image_processed.jpg'):
            os.remove('image_processed.jpg')
        src2 = self.qimg2cv(self.Qimg)
        Image = self.change_brightness(src2,self.brightness)
        cv2.imwrite("image_processed.jpg",Image)
        self.Qimg = QImage('image_processed.jpg')
        if os.path.exists('image_processed.jpg'):
            os.remove('image_processed.jpg')
        self.brightnessChanged.emit(1)

    def change_brightness(self, img, value=0):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v,int(value/2))
        v[v > 255] = 255
        v[v < 0] = 0
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img
    
    def ChangeC(self):
        if self.contrast > 0:
            self.contrast = (self.contrast / QtCore.QSize().width())+2
        elif self.contrast < 0:
            self.contrast = -self.contrast/QtCore.QSize().width()
        src1 = self.qimg2cv(self.grayscale_image)
        adjusted = cv2.convertScaleAbs(src1,self.contrast,0)
        cv2.imwrite('image_processed.jpg',adjusted)
        self.setPixmap(QPixmap.fromImage(QImage('image_processed.jpg')))
        if os.path.exists('image_processed.jpg'):
            os.remove('image_processed.jpg')
        src2 = self.qimg2cv(self.Qimg)
        adjusted = cv2.convertScaleAbs(src2,self.contrast,0)
        cv2.imwrite('image_processed.jpg',adjusted)
        self.Qimg = QImage('image_processed.jpg')
        if os.path.exists('image_processed.jpg'):
            os.remove('image_processed.jpg')
        self.contrastChanged.emit(1)
    
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
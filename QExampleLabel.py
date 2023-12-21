import sys
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect


class QExampleLabel (QLabel):
    def __init__(self, parentQWidget = None):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.isCropable = False
        self.currentQRubberBand = None

    def setImage (self,pixmap):
        self.setPixmap(pixmap)

    def removeImage(self):
        QLabel.clear()

    def setIsCropable(self,bool):
        self.isCropable = bool

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
        cropQPixmap = self.pixmap().copy(currentQRect)
        cropQPixmap.save('output.png')

if __name__ == '__main__':
    myQApplication = QApplication(sys.argv)
    myQExampleLabel = QExampleLabel()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
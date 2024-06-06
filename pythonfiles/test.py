from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor
from PyQt5.QtCore import Qt, QRectF
import sys

class ImageWidget(QWidget):
    def __init__(self):
        super(ImageWidget,self).__init__()

        # Load the image into the QLabel
        self.image_label = QLabel(self)
        pixmap = QPixmap("1.jpg")  # Replace with the path to your image
        self.image_label.setPixmap(pixmap)

        # Define the rectangle to clear (replace these values with your desired coordinates and dimensions)
        self.rect = QRectF(50, 50, 100, 100)

        # Call the function to modify and update the image
        self.modify_image()

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

    def modify_image(self):
        # Get the image from the QLabel
        image = self.image_label.pixmap().toImage()

        # Clear the specified rectangle in the image
        self.clear_rect(image, self.rect)

        # Save the modified image to a file (replace "path_to_modified_image.jpg" with the desired path)
        image.save("wadawd.png")

    def clear_rect(self, image, rect):
        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(rect, Qt.transparent)
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ImageWidget()
    widget.show()
    sys.exit(app.exec_())
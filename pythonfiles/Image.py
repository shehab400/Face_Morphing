import numpy as np
from PyQt5.QtGui import QPixmap,QImage
import matplotlib.pyplot as plt
class Image:
    def __init__(self):
        self.path = ""
        self.raw_data = None
        self.imagelabel=0            
        # Get size
        self.shape = None
        self.freqx = None
        self.freqy = None
        self.width = 0
        self.height = 0
        self.original_image = None
        self.fft = None
        # Get magnitude
        self.magnitude = None
        # Get phase
        self.phase = None
        # Get real
        self.real = None
        # Get imag
        self.imaginary = None
        self.type=None
        self.pixmap=None
        self.grayscale=None
        self.key=0
    
        # self.pixmap = None
        # self.components = dict()

    def imageInitializer(self,path,imglabel):
        self.imagelabel=imglabel
        self.path = path
        self.original_image = QImage(self.path)
        grayscale_image = self.original_image.convertToFormat(QImage.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(grayscale_image)
        self.grayscale = grayscale_image
        raw_data = plt.imread(self.path)
        raw_data = raw_data.astype('float32')
        raw_data /= 255
        self.raw_data=raw_data
        self.raw_data = np.mean(raw_data, axis=-1)
        self.shape = self.raw_data.shape
        self.width = self.shape[1]
        self.height = self.shape[0]
        self.freqx = np.fft.fftfreq(self.shape[0])
        self.freqy = np.fft.fftfreq(self.shape[1])
        fft = np.fft.fft2(self.raw_data)
        self.fft = np.fft.fftshift(fft)
        print(self.fft.shape)
        self.magnitude = np.abs(self.fft)
        self.phase = np.angle(self.fft)
        self.real = np.real(self.fft)
        self.imaginary = np.imag(self.fft)

    def copy(self):
        img = Image()
        img.path = self.path
        img.raw_data = self.raw_data
        img.imagelabel = self.imagelabel
        img.shape = self.shape
        img.freqx = np.fft.fftfreq(img.shape[0])
        img.freqy = np.fft.fftfreq(img.shape[1])
        img.width = self.width
        img.height = self.height
        img.fft = self.fft.copy()
        img.magnitude = self.magnitude.copy()
        img.phase = self.phase.copy()
        img.real = self.real.copy()
        img.imaginary = self.imaginary.copy()
        img.type = self.type
        img.pixmap = None
        img.grayscale = None
        img.key = self.key
        return img
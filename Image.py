import numpy as np
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
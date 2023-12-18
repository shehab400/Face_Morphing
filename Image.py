class Image:
    def __init__(self):
        self.path = ""
        self.raw_data = None
                    
        # Get size
        self.shape = None
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

        # self.pixmap = None
        # self.components = dict()
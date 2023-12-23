from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import time

class Worker(QObject):
    progress = Signal(int)
    start = Signal(int)
    completed = Signal(int)
    end = False
    @Slot(int)
    def do_work(self,n):
        if self.end == False:
            self.start.emit(n)

    def working(self,n):
        if self.end == False:
            time.sleep(0.1)
            self.progress.emit(n)

    def done(self):
        self.end = True
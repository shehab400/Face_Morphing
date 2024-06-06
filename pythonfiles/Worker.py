from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
import time

class Worker(QObject):
    progress = Signal(int)
    completed = Signal(int)
    end = False

    @Slot(int)
    def do_work(self, n):
        for i in range(1, n+1):
            if self.end == True:
                return
            time.sleep(0.5)
            if self.end == True:
                return
            self.progress.emit(i)

        self.completed.emit(i)
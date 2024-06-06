from myWindow import *
import qdarkstyle
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  
    window = MyWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window.show()
    sys.exit(app.exec_()) 
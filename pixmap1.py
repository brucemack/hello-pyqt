import sys
import colorsys
import math
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

def make_color_from_intensity(intensity):
    c = colorsys.hls_to_rgb(0.6, intensity, 1.0)
    return QColor(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(320, 240)
        canvas.fill(Qt.black)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw_something()
        self.draw_something()
        self.draw_something()
        
        # creating a timer object
        timer = QTimer(self)
 
        # adding action to timer
        timer.timeout.connect(self.tick)
 
        # update the timer every second
        timer.start(100)
 
    def add_line(self, qp, data):
        # Shift up existing 
        self.label.pixmap().scroll(0, -1, 0, 0, 320, 240)
        # Draw new line
        for x in range(0, len(data)):
            pen = QPen(make_color_from_intensity(data[x]), 2, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawPoint(x, 239)           

    def draw_something(self):

        qp = QtGui.QPainter(self.label.pixmap())
        #pen = QPen(QColor(168, 34, 3), 4, Qt.SolidLine)
        #qp.setPen(pen)
        #qp.drawLine(0, 200, 100, 200)

        data = [0] * 100
        for t in range(0, 100):
            phi = (float(t) / 100.0) * 8.0 * 3.14159
            data[t] = (1.5 + math.cos(phi)) / 3.0

        self.add_line(qp, data)

        qp.end()

        #exposed = QtGui.QRegion()
        #self.label.pixmap().scroll(0, 50, 0, 0, 100, 100)

    # method called by timer
    def tick(self): 
        self.draw_something()
        self.update() 

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

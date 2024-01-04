import sys
import colorsys
import math
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

def make_color_from_intensity(intensity):
    """ The intensity should be from 0.0 to 1.0
    """
    if intensity < 0 or intensity > 1.0:
        raise Exception("Intensity is out of range")
    c = colorsys.hls_to_rgb(0.6, intensity, 1.0)
    return QColor(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

def force_range(x, min_x, max_x):
    if x < min_x:
        return min_x
    elif x > max_x:
        return max_x
    else:
        return x

def rescale(data, target_length):
    """ Takes a list of data points and creates a new set of data points with the specified 
        target_length.  Does downsampling/upsampling as needed to adjust the data length.
    """
    source_length = float(len(data))
    result = [0] * target_length
    # This is the number of input samples that are used for each output
    sample_ratio = source_length / float(target_length)
    # Sweep over the target range
    for target_x in range(0, target_length):
        # What fraction of the range are we at?
        fract = float(target_x) / float(target_length)
        # When the sample ratio is less than two then there is no 
        # interpolation to do.
        if sample_ratio < 2.0:
            source_x = int(source_length * fract)
            result[target_x] = data[source_x]
        # When the sample ration is more than two then we average across 
        # the relevant source samples.
        else:
            avg = 0
            avg_points = 0
            for i in range(0, int(sample_ratio)):
                source_x = int((source_length * fract) - (sample_ratio / 2.0) + float(i))
                avg = avg + data[force_range(source_x, 0, len(data) - 1)]
                avg_points = avg_points + 1
            result[target_x] = avg / float(avg_points)
    return result


class Waterfall:

    def __init__(self, pixmap, x, y, w, h):
        self.pixmap = pixmap
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def add_line(self, data):
        # First convert the data to a scaled data using interpolation
        scaled_data = rescale(data, self.w)
        # Render
        # Shift up existing content by one pixel
        self.pixmap.scroll(0, -1, self.x, self.y, self.w, self.h)
        qp = QtGui.QPainter(self.pixmap)
        # Draw new line
        for i in range(0, self.w):
            if i < len(scaled_data):
                pen = QPen(make_color_from_intensity(scaled_data[i]), 1, Qt.SolidLine)
                qp.setPen(pen)
                # We are drawing on the bottom row
                qp.drawPoint(i, self.h - 1)           
        qp.end()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(320, 240)
        canvas.fill(Qt.black)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.waterfall = Waterfall(self.label.pixmap(), 0, 0, 320, 200)
        
        # creating a timer object
        timer = QTimer(self)
 
        # adding action to timer
        timer.timeout.connect(self.tick)
 
        # update the timer every second
        timer.start(100)
 
        self.h = 8.0
        self.dh = 0.0

    def draw_something(self):
        data = [0] * 50
        for t in range(0, 50):
            phi = (float(t) / 50.0) * self.h * 3.14159
            data[t] = (1.5 + math.cos(phi)) / 3.0
        self.waterfall.add_line(data)
        self.update() 

        self.h  = self.h + self.dh
 
    # method called by timer
    def tick(self): 
        self.draw_something()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

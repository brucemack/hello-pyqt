import sys
import colorsys
import math
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPolygonF

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
        
    def add_line(self, qp, data):
        # First convert the data to a scaled data using interpolation
        scaled_data = rescale(data, self.w)
        # Shift up existing content by one pixel
        self.pixmap.scroll(0, -1, self.x, self.y, self.w, self.h)
        # Draw new line at the bottom of the view
        for i in range(0, self.w):
            pen = QPen(make_color_from_intensity(scaled_data[i]), 1, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawPoint(i, self.h - 1)           

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.w = 320
        self.h = 240
        self.f_mhz = 0

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(self.w, self.h)
        canvas.fill(Qt.black)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.waterfall = Waterfall(self.label.pixmap(), 0, 0, self.w, self.h - 50)

        # creating a timer object
        timer = QTimer(self)
 
        # adding action to timer
        timer.timeout.connect(self.tick)
 
        # update the timer every second
        #timer.start(1000)
 
    def draw_legend(self, qp):

        qp.fillRect(0, self.h - 50, self.w, 50, Qt.black)

        # Setup the border/legend at the bottom
        pen = QPen(Qt.white, 1, Qt.SolidLine)
        qp.setPen(pen)
        # Horizontal line       
        qp.drawLine(0, self.h - 50, self.w, self.h - 50)
        # Frequency tick
        qp.drawLine(int(self.w / 2), self.h - 50, int(self.w / 2), self.h - 40)

        # Cursor
        cursor_x = 100
        
        polygon = QPolygonF() 
        polygon.append(QtCore.QPointF(cursor_x, self.h - 49))  
        polygon.append(QtCore.QPointF(cursor_x + 10, self.h - 40))  
        polygon.append(QtCore.QPointF(cursor_x - 10, self.h - 40))  
        polygon.append(QtCore.QPointF(cursor_x, self.h - 49))  
        brush = QtGui.QBrush(Qt.white)
        qp.setBrush(brush)
        qp.drawPolygon(polygon)
        
        f = qp.font()
        f.setPixelSize(10)
        qp.setFont(f)
        f_khz = int(self.f_mhz / 1000)
        t = f"{f_khz:,}" 
        qp.drawText(0, self.h - 35, 100, 10, Qt.AlignLeft, t)
 
    # method called by timer
    def tick(self): 
        pass

    def set_freq(self, f_mhz):
        self.f_mhz = f_mhz

    def process_line(self, line):
        if not line.startswith("[WF]"):
            return
        tokens = line[4:].split(",")
        if len(tokens) <= 2:
            return

        self.set_freq(float(tokens[0]))
        max_mag = float(tokens[1])

        data = []
        for i in range(2, len(tokens)):
            data.append(float(tokens[i]) / max_mag)

        qp = QtGui.QPainter(self.label.pixmap())
        self.waterfall.add_line(qp, data)
        self.draw_legend(qp)
        qp.end()
        self.update() 

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
window.process_line("[WF]7000000,1.0,1.0,0.57,0.5,1.0")
window.process_line("[WF]7000000,1.0,1.0,0.57,0.5,1.0")
window.process_line("[WF]7000000,1.0,1.0,0.57,0.5,1.0")

app.exec_()

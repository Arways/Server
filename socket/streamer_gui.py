# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

import socket
import cv2
import numpy
import time
import base64
import sys
from datetime import datetime
class ClientSocket(QThread):
    def __init__(self, ip, port, parent, input_video_label):
        super().__init__(parent)
        self.input_video_label = input_video_label
        self.parent = parent
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0

    def connectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            self.sendImages()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(u'Connect fail %d times. exit program'%(self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server'%(self.connectCount))
            self.connectServer()

    def sendImages(self):
        cnt = 0
        capture = cv2.VideoCapture("input/short.mp4")
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 315)
        try:
            while capture.isOpened():
                ret, frame = capture.read()
                resize_frame = cv2.resize(frame, dsize=(480, 315), interpolation=cv2.INTER_AREA)
                
                img = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                qImg = QtGui.QImage(img.data, 480, 315, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.input_video_label.setPixmap(pixmap)
                
                now = time.localtime()
                stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                result, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
                data = numpy.array(imgencode)
                stringData = base64.b64encode(data)
                length = str(len(stringData))
                self.sock.sendall(length.encode('utf-8').ljust(64))
                self.sock.send(stringData)
                self.sock.send(stime.encode('utf-8').ljust(64))
                print(u'send images %d'%(cnt))
                cnt+=1
                time.sleep(0.095)

        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.connectServer()
            self.sendImages()
            
    def run(self):
        self.connectServer()
            

class Ui_MainWindow(object):
    def button_clicked(self):
        TCP_IP = '10.0.0.4'
        TCP_PORT = 8080
        t = ClientSocket(TCP_IP, TCP_PORT, self.MainWindow, self.input_video_label)
        t.start()
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Streamer_GUI")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.input_video_label = QtWidgets.QLabel(self.centralwidget)
        self.input_video_label.setGeometry(QtCore.QRect(80, 40, 480, 315))
        self.input_video_label.setObjectName("input_video_label")
        self.strat_stream_button = QtWidgets.QPushButton(self.centralwidget)
        self.strat_stream_button.setGeometry(QtCore.QRect(290, 440, 211, 71))
        self.strat_stream_button.setObjectName("strat_stream_button")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.MainWindow = MainWindow

        self.retranslateUi(MainWindow)
        self.strat_stream_button.clicked.connect(self.button_clicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.input_video_label.setText(_translate("MainWindow", "TextLabel"))
        self.strat_stream_button.setText(_translate("MainWindow", "Start Streaming"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


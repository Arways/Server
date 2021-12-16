# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'streamer_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import socket
import cv2
import numpy
import time
import base64
import sys
from datetime import datetime

class ClientSocket(QThread):
    def __init__(self, ip, port, parent, input_video_label, log_edit):
        super().__init__(parent)
        self.input_video_label = input_video_label
        self.log_edit = log_edit
        self.parent = parent
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.power=True

    def connectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print('Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.log_edit.append('Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            self.sendImages()
        except Exception as e:
            #self.log_edit.append(str(e))
            self.connectCount += 1
            if self.connectCount == 10:
                print('Connect fail %d times'%(self.connectCount))
                self.log_edit.append('Connect fail %d times'%(self.connectCount))
                self.quit()
            else:
                print('%d times try to connect with server'%(self.connectCount))
                self.log_edit.append('%d times try to connect with server'%(self.connectCount))
                self.connectServer()


    def sendImages(self):
        cnt = 0
        #capture = cv2.VideoCapture("input/short.mp4")
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 256)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 192)
        try:
            while capture.isOpened() and self.power:
                ret, frame = capture.read()
                resize_frame = cv2.resize(frame, dsize=(256, 192), interpolation=cv2.INTER_AREA)
                
                img = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                qImg = QtGui.QImage(img.data, 256, 192, QtGui.QImage.Format_RGB888)
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
                time.sleep(0.0095)

        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.connectServer()
            #self.sendImages()
            
    def run(self):
        self.power=True
        self.connectServer()
        
    def stop(self):
        self.power=False
        self.connectCount = 0
        self.quit()
        
class ClientCam(QThread):
    def __init__(self, parent, input_video_label):
        super().__init__(parent)
        self.input_video_label = input_video_label
        self.power=True

    def showImage(self):
        #capture = cv2.VideoCapture("input/short.mp4")
        capture = cv2.VideoCapture(0)
        #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 256)
        #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 192)
        width = 256
        height = 192
        try:
            while capture.isOpened() and self.power :
                ret, frame = capture.read()
                resize_frame = cv2.resize(frame, dsize=(width, height), interpolation=cv2.INTER_AREA)
                
                img = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                qImg = QtGui.QImage(img.data, width, height, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.input_video_label.setPixmap(pixmap)

        except Exception as e:
            self.showImage()
            
    def run(self):
        self.power=True
        self.showImage()
        
    def stop(self):
        self.power=False
        self.quit()

class Ui_MainWindow(object):
    
    def start_streaming(self):
        self.clientCam.stop()
        self.start_stream_button.setEnabled(False)
        self.stop_stream_button.setEnabled(True)
        self.clientSocekt.start()
        
    def stop_streaming(self):
        self.clientSocekt.stop()
        self.start_stream_button.setEnabled(True)
        self.stop_stream_button.setEnabled(False)
        self.clientCam.start()
        
    def add_broad(self):
        str = self.broad_name_edit.text()
        self.rooms.append(str)
        self.broad_name_edit.clear()
        self.showList()
        
        TCP_IP = self.broad_ip_edit.text()
        TCP_PORT = int(self.broad_port_edit.text())
        self.clientSocekt = ClientSocket(TCP_IP, TCP_PORT, self.MainWindow, self.input_video_label, self.log_edit)
        
        self.broad_ip_edit.setEnabled(False)
        self.broad_port_edit.setEnabled(False)
        self.broad_add_button.setEnabled(False)
        self.broad_list_view.setEnabled(False)
        self.broad_name_edit.setEnabled(False)
        self.start_stream_button.setEnabled(True)
        self.clientCam.start()
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(859, 410)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.input_video_label = QtWidgets.QLabel(self.centralwidget)
        self.input_video_label.setGeometry(QtCore.QRect(280, 10, 381, 261))
        self.input_video_label.setFrameShape(QtWidgets.QFrame.Box)
        self.input_video_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.input_video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.input_video_label.setObjectName("input_video_label")
        self.start_stream_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_stream_button.setGeometry(QtCore.QRect(280, 280, 181, 71))
        self.start_stream_button.setObjectName("start_stream_button")
        self.broad_list_view = QtWidgets.QListView(self.centralwidget)
        self.broad_list_view.setGeometry(QtCore.QRect(10, 10, 261, 251))
        self.broad_list_view.setObjectName("broad_list_view")
        self.broad_add_button = QtWidgets.QPushButton(self.centralwidget)
        self.broad_add_button.setGeometry(QtCore.QRect(190, 330, 81, 23))
        self.broad_add_button.setObjectName("broad_add_button")
        self.broad_name_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.broad_name_edit.setGeometry(QtCore.QRect(10, 330, 171, 20))
        self.broad_name_edit.setObjectName("broad_name_edit")
        self.stop_stream_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_stream_button.setGeometry(QtCore.QRect(470, 280, 191, 71))
        self.stop_stream_button.setObjectName("stop_stream_button")
        self.log_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.log_edit.setGeometry(QtCore.QRect(670, 10, 171, 341))
        self.log_edit.setObjectName("log_edit")
        self.broad_ip_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.broad_ip_edit.setGeometry(QtCore.QRect(10, 270, 261, 20))
        self.broad_ip_edit.setObjectName("broad_ip_edit")
        self.broad_port_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.broad_port_edit.setGeometry(QtCore.QRect(10, 300, 261, 20))
        self.broad_port_edit.setObjectName("broad_port_edit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 859, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.MainWindow = MainWindow

        self.retranslateUi(MainWindow)
        self.start_stream_button.clicked.connect(self.start_streaming)
        self.broad_add_button.clicked.connect(self.add_broad)
        self.stop_stream_button.clicked.connect(self.stop_streaming)
        self.rooms = ['Room1', 'Room2', 'Room3', 'Room4']
        self.showList()
        self.broad_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.start_stream_button.setEnabled(False)
        self.stop_stream_button.setEnabled(False)
        self.log_edit.setEnabled(False)
        
        self.clientCam = ClientCam(self.MainWindow, self.input_video_label)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.input_video_label.setText(_translate("MainWindow", "<html><head/><body><p>Waiting for Starting Streaming...</p></body></html>"))
        self.start_stream_button.setText(_translate("MainWindow", "Start Streaming"))
        self.broad_add_button.setText(_translate("MainWindow", "Add Room"))
        self.broad_name_edit.setText(_translate("MainWindow", "Name"))
        self.stop_stream_button.setText(_translate("MainWindow", "Stop Streaming"))
        self.broad_ip_edit.setText(_translate("MainWindow", "localhost"))
        self.broad_port_edit.setText(_translate("MainWindow", "8080"))
        
    def showList(self):
        self.model = QStandardItemModel()
        for room in self.rooms:
            self.model.appendRow(QStandardItem(room))
        self.broad_list_view.setModel(self.model)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!
import os
import sys


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

from Hrnet.pose_estimation.video import getTwoModel, getKptsFromImage
detect2d = getKptsFromImage

from Videopose3D.common.model import RIEModel, TemporalModel
from Videopose3D.common.generators import UnchunkedGenerator
from Videopose3D.common.camera import camera_to_world, normalize_screen_coordinates
import util 
common = util.common

import socket
import cv2
import numpy as np
import base64
import glob
import time
import threading
import torch
from datetime import datetime
import timeit

class EstimatePose:
    def __init__(self):
        self.cur_frame = 0
        self.frame_width = 0
        self.frame_height = 0
        self.frame_len = 10
        
        print("preparing Hrnet...")
        self.bboxModel, self.poseModel = getTwoModel()
        
        print("preparing VideoPose3D...")
        chk_point_path = 'Videopose3D/checkpoint/pretrained_h36m_detectron_coco.bin'
        self.model_pos = TemporalModel(17,2,17,filter_widths=[3,3,3,3,3],causal=False,dropout=False)
        chk_point = torch.load(chk_point_path)
        self.model_pos = self.model_pos.cuda()
        self.model_pos.load_state_dict(chk_point['model_pos'])
        
        self.keypoints_2d = []
        self.last_keypoint_2d = None
        print("preparing Done")

    def evaluate(self,test_generator, model_pos, action=None, return_predictions=False):
        joints_left, joints_right = list([4, 5, 6, 11, 12, 13]), list([1, 2, 3, 14, 15, 16])
        with torch.no_grad():
            model_pos.eval()
            N = 0
            for _, batch, batch_2d in test_generator.next_epoch():
                inputs_2d = torch.from_numpy(batch_2d.astype('float32'))
                if torch.cuda.is_available():
                    inputs_2d = inputs_2d.cuda()
                # Positional model
                predicted_3d_pos = model_pos(inputs_2d)
                if test_generator.augment_enabled():
                    # Undo flipping and take average with non-flipped version
                    predicted_3d_pos[1, :, :, 0] *= -1
                    predicted_3d_pos[1, :, joints_left + joints_right] = predicted_3d_pos[1, :, joints_right + joints_left]
                    predicted_3d_pos = torch.mean(predicted_3d_pos, dim=0, keepdim=True)
                if return_predictions:
                    return predicted_3d_pos.squeeze(0).cpu().numpy()
                
    def detect3d(self,predictor, input_kps, W, H):
        input_kps = normalize_screen_coordinates(input_kps[..., :2], w=W, h=H)
        keypoints = input_kps.copy()
        
        gen = UnchunkedGenerator(None, None, [keypoints], pad=common.pad, causal_shift=common.causal_shift, augment=True, kps_left=common.kps_left, kps_right=common.kps_right, joints_left=common.joints_left, joints_right=common.joints_right)
        prediction = self.evaluate(gen, predictor, return_predictions=True)
        prediction = camera_to_world(prediction, R=common.rot, t=0)
        prediction[:,:,2] -= np.min(prediction[:,:,2])
        return prediction    
    
    def estimate(self,frame):
        keypoint = detect2d(self.bboxModel, self.poseModel, frame)
        if isinstance(keypoint, np.ndarray):
            self.last_keypoint_2d = keypoint.copy()
            
        self.keypoints_2d.append(self.last_keypoint_2d)
        
        if self.keypoints_2d.__len__() < self.frame_len+1:
            self.frame_height = frame.shape[0]
            self.frame_width = frame.shape[1]
            return None, None
        
        self.keypoints_2d.pop(0)
        keypoints_3d = self.detect3d(self.model_pos, np.array(self.keypoints_2d),self.frame_width,self.frame_height)
        keypoint_3d = keypoints_3d[-1]
        
        #pose_img = util.draw_3Dimg(keypoint_3d, frame, display=0, kpt2D=self.last_keypoint_2d)
        return keypoint_3d, self.last_keypoint_2d
        
    
class ServerSocket(QThread):
    
    def __init__(self, ip, port, parent, received_video_label, pose_label):
        super().__init__(parent)
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.received_video_label = received_video_label
        self.pose_label = pose_label
        self.estimatePose = EstimatePose()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(4)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
       # while 1:
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

    def receiveImages(self):

        try:
            while True:
                length = self.recvall(self.conn, 64)
                length1 = length.decode('utf-8')
                stringData = self.recvall(self.conn, int(length1))
                stime = self.recvall(self.conn, 64)
                print('send time: ' + stime.decode('utf-8'))
                now = time.localtime()
                print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                data = np.frombuffer(base64.b64decode(stringData), np.uint8)
                decimg = cv2.imdecode(data, 1)
                #cv2.imshow("server", decimg)
                #key = cv2.waitKey(1)
                #if key == 27:
                #    break


                keypoint_3d, last_keypoint_2d = self.estimatePose.estimate(decimg)
                '''
                if poseImg:
                    width = poseImg.shape[0]
                    height = poseImg.shape[1]
                    qImg = QtGui.QImage(decimg.data, width, height, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(qImg)
                    self.pose_label.setPixmap(pixmap)
                '''
                
                #print(keypoint_3d)
                
                '''
                width = decimg.shape[0]
                height = decimg.shape[1]
                qImg = QtGui.QImage(decimg.data, height, width, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.received_video_label.setPixmap(pixmap)
                '''
                
                
                if keypoint_3d is not None:
                    img_3d = util.draw_3Dimg(keypoint_3d, decimg, display=False, kpt2D=last_keypoint_2d)

                    width = img_3d.shape[0]
                    height = img_3d.shape[1]
                    qImg = QtGui.QImage(img_3d.data, height, width, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(qImg)
                    self.received_video_label.setPixmap(pixmap)
                


        except Exception as e:
            print(e)
            self.socketClose()
            cv2.destroyAllWindows()
            self.socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def run(self):
        self.socketOpen()
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()
        
        '''
        self.socketOpen()
        self.receiveThread2 = threading.Thread(target=self.receiveImages)
        self.receiveThread2.start()
        '''
    

class Ui_MainWindow(object):
    def button_clicked(self):
        self.t.start()
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Server_GUI")
        MainWindow.resize(1200, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.received_video_label = QtWidgets.QLabel(self.centralwidget)
        self.received_video_label.setGeometry(QtCore.QRect(0, 0, 1500, 400))
        self.received_video_label.setObjectName("received_video_label")
        self.pose_label = QtWidgets.QLabel(self.centralwidget)
        self.pose_label.setGeometry(QtCore.QRect(390, 80, 351, 261))
        self.pose_label.setObjectName("pose_label")
        self.start_server_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_server_button.setGeometry(QtCore.QRect(270, 430, 261, 61))
        self.start_server_button.setObjectName("start_server_button")
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
        self.start_server_button.clicked.connect(self.button_clicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        TCP_IP = 'localhost'
        TCP_PORT = 8080
        self.t = ServerSocket(TCP_IP, TCP_PORT, self.MainWindow, self.received_video_label, self.pose_label)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.received_video_label.setText(_translate("MainWindow", ""))
        self.pose_label.setText(_translate("MainWindow", ""))
        self.start_server_button.setText(_translate("MainWindow", "Start Server"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


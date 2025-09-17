import sys, os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, QUrl
import QtCreator as QtC
import ReceiveFeed
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
RASPBERRYPI_IP = os.getenv('RASPBERRYPI_IP')

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        #self.ui = QtC.Ui_MainWindow()
        #self.ui.setupUi(self)
        
        self.setWindowTitle("Raspberry Pi Camera Feed")
        self.setGeometry(100, 100, 640, 480) #initial window size
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Waiting for video feed")
        self.image_label.setStyleSheet("background-color: lightgray;")

        vbox = QVBoxLayout(self.central_widget)
        vbox.addWidget(self.image_label)

        if not RASPBERRYPI_IP:
            print(f"Error: Raspberry Pi IP ({RASPBERRYPI_IP}) is not found in .env file or is empty.")
            self.image_label.setText(f"Error: Raspberry Pi IP ({RASPBERRYPI_IP}) is not configured.")
        
        self.stream_url = QUrl(f"http://{RASPBERRYPI_IP}:5000/video_feed")

        self.video_thread = ReceiveFeed.VideoStreamThread(self.stream_url)
        self.video_thread.changePixmap.connect(self.update_image)
        self.video_thread.start()

    def update_image(self, pixmap):
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def closeEvent(self, event):
        self.video_thread.stop()
        event.accept()
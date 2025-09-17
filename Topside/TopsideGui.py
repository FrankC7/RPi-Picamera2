import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
import QtCreator as QtC

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = QtC.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.pushButton.clicked.connect(self.action)
    
    def action(self):
        print("Button clicked")
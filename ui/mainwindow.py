#!/usr/bin/env python

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ui.ui_mainwindow import Ui_MainWindow
class MainWindow (QMainWindow):
    def __init__(self):
        super().__init__()

        file = QFile("ui/mainwindow.ui")
        file.open(QFile.ReadOnly)
        loader = QUiLoader(parent = self)
        ui = loader.load(file)
        file.close()
        self.setCentralWidget(ui)

        #self.ui = Ui_MainWindow()
        #self.ui.setupUi(self)
        #self.connect_menu_items()
    
    def connect_menu_items (self):
        self.ui.action_exit.triggered.connect(self.close)

    def closeEvent (self, event):
        print("HogeHoge")


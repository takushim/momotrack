#!/usr/bin/env python

from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow (QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        ui_file = QFile("ui/mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.window.show()


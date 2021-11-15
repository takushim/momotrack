#!/usr/bin/env python

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow:
    def __init__(self):
        self.ui_window = self.load_ui()
        self.ui_window.show()
    
    def load_ui (self):
        ui_file = QFile("ui/mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        ui_window = QUiLoader().load(ui_file)
        ui_file.close()
        return ui_window


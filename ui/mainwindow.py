#!/usr/bin/env python

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

def load_ui (self):
    file = QFile("ui/mainwindow.ui")
    file.open(QFile.ReadOnly)
    loader = QUiLoader()
    ui = loader.load(file)
    file.close()
    return ui

class MainWindow (QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = load_ui("ui/mainwindow.ui")
        self.setCentralWidget(self.ui)
        self.connect_menu_items()
        self.image_filename = None
        self.track_filename = None
        self.track_modified = False

    def connect_menu_items (self):
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)

    def slot_about_this (self):
        mbox = QMessageBox()
        mbox.setWindowTitle("About This")
        mbox.setText("Object tracking system for time-lapse 2D/3D images.\n" +
                     "Copyright 2021 by Takushi Miyoshi (NIH/NIDCD).")
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def closeEvent (self, event):
        if self.track_modified:
            mbox = QMessageBox()
            mbox.setWindowTitle("Save Track?")
            mbox.setText("Tracking record modified. Save?")
            mbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mbox.setDefaultButton(QMessageBox.Cancel)
            result = mbox.exec()
            if result == QMessageBox.Save:
                pass
            elif result == QMessageBox.Discard:
                pass
            else:
                event.ignore()

    



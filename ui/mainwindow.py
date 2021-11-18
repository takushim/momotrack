#!/usr/bin/env python

from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from etc import imagestack

def load_ui (filename):
    file = QFile(filename)
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
        self.tracks_filename = None
        self.tracks_modified = False

    def connect_menu_items (self):
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_tracks.triggered.connect(self.slot_load_tracks)
        self.ui.action_save_tracks.triggered.connect(self.slot_save_tracks)
        self.ui.action_save_tracks_as.triggered.connect(self.slot_save_tracks_as)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_quick_help.triggered.connect(self.slot_quick_help)
    
    def open_image (self):
        pass

    def load_tracks (self):
        pass

    def save_tracks (self):
        ## save here
        self.tracks_modified = False

    def slot_open_image (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select an image to open.")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["Images (*.tiff *.tif *.stk)", "Any (*.*)"])
        dialog.setViewMode(QFileDialog.List)
        dialog.exec()
        # open image here
        print(dialog.selectedFiles())

    def slot_load_tracks (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a tracking record to load.")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["JSON file (*.json)", "Any (*.*)"])
        dialog.setViewMode(QFileDialog.List)
        dialog.exec()
        # load image here
        print(dialog.selectedFiles())

    def slot_save_tracks (self):
        if self.tracks_filename is None:
            self.slot_save_tracks_as()
        else:
            self.save_tracks()

    def slot_save_tracks_as (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a filename to save the tracking record.")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(["JSON file (*.json)", "Any (*.*)"])
        dialog.setViewMode(QFileDialog.List)
        result = dialog.exec()
        if result == QFileDialog.Save:
            print(dialog.selectedFiles())
            self.save_tracks()

    def slot_quick_help (self):
        mbox = QMessageBox()
        mbox.setWindowTitle("Quick help")
        mbox.setText("Currently nothing to show...")
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def slot_about_this (self):
        mbox = QMessageBox()
        mbox.setWindowTitle("About This")
        mbox.setText("Object tracking system for time-lapse 2D/3D images.\n" +
                     "Copyright 2021 by Takushi Miyoshi (NIH/NIDCD).")
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def closeEvent (self, event):
        if self.tracks_modified:
            mbox = QMessageBox()
            mbox.setWindowTitle("Save Track?")
            mbox.setText("Tracking record modified. Save?")
            mbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mbox.setDefaultButton(QMessageBox.Cancel)
            result = mbox.exec()
            if result == QMessageBox.Cancel:
                event.ignore()
            elif result == QMessageBox.Discard:
                event.accept()
            else:
                if self.track_filename is None:
                    self.slot_save_tracks_as()
                else:
                    self.slot_save_tracks()
                if self.track_modified:
                    event.ignore()

    



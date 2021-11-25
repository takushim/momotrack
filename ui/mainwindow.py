#!/usr/bin/env python

import sys
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QGraphicsScene
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ui import imagepanel, lutpanel
from image import imagestack

def test_func (event):
    print(event.scenePos())

class MainWindow (QMainWindow):
    def __init__ (self, image_filename = None, track_filename = None):
        super().__init__()
        self.image_stack = None
        self.image_filename = image_filename
        self.track_filename = track_filename
        self.track_modified = False

        self.load_ui()
        self.connect_menu_signals()

        if self.image_filename is not None:
            self.load_image()
        if self.track_filename is not None:
            self.load_tracks()

    def load_ui (self):
        file = QFile("ui/mainwindow.ui")
        file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui)
        self.scene = QGraphicsScene()
        self.scene.mousePressEvent = test_func

    def connect_menu_signals (self):
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_tracks.triggered.connect(self.slot_load_tracks)
        self.ui.action_save_tracks.triggered.connect(self.slot_save_tracks)
        self.ui.action_save_tracks_as.triggered.connect(self.slot_save_tracks_as)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_quick_help.triggered.connect(self.slot_quick_help)

    def load_image (self):
        try:
            self.stack = imagestack.ImageStack(self.image_filename)
            imagepanel.set_sliders(self.ui, self.stack)
            imagepanel.update_status(self.ui, self.stack)
            imagepanel.update_image_view(self.ui, self.scene, self.stack)
        except FileNotFoundError:
            self.show_message(title = "Image loading error", message = "Failed to load image: {0}".format(self.image_filename))

    def load_tracks (self):
        pass

    def save_tracks (self):
        ## save here
        self.track_modified = False

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
        if self.track_filename is None:
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
        self.show_message(title = "Quick help", message = "Currently nothing to show...")

    def slot_about_this (self):
        self.show_message(title = "About This",
                          message = "Object tracking system for time-lapse 2D/3D images.\n" +
                                    "Copyright 2021 by Takushi Miyoshi (NIH/NIDCD).")

    def closeEvent (self, event):
        if self.track_modified:
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

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    



#!/usr/bin/env python

from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QSlider
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from image import imagestack

class MainWindow (QMainWindow):
    def __init__(self, image_filename = None, track_filename = None):
        super().__init__()
        self.image_stack = None
        self.image_filename = image_filename
        self.track_filename = track_filename
        self.track_modified = False

        self.load_ui()
        self.connect_menu_items()
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

    def connect_menu_items (self):
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
            # Time slider
            self.ui.slider_time.setMinimum(0)
            self.ui.slider_time.setMaximum(self.stack.t_count - 1)
            self.ui.slider_time.setValue(0)
            self.ui.slider_time.setTickInterval(10)
            self.ui.slider_time.setTickPosition(QSlider.TicksBelow)
            # Z slider
            self.ui.slider_zstack.setMinimum(0)
            self.ui.slider_zstack.setMaximum(self.stack.t_count - 1)
            self.ui.slider_zstack.setValue(0)
            self.ui.slider_zstack.setTickInterval(10)
            self.ui.slider_zstack.setTickPosition(QSlider.TicksBelow)
            # Status
            self.update_status()
        except Exception as e:
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

    def update_status (self):
        status = "T: {0}/{1}, Z: {2}/{3}".format(self.ui.slider_time.value(), self.stack.t_count - 1,
                                                 self.ui.slider_zstack.value(), self.stack.z_count - 1,)
        self.ui.label_status.setText(status)

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    



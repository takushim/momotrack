#!/usr/bin/env python

import sys
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from ui import imagepanel, zoompanel, lutpanel
from image import stack

class MainWindow (QMainWindow):
    def __init__ (self, image_filename = None, track_filename = None):
        super().__init__()
        self.app_name = "PyTrace"

        self.image_filename = image_filename
        self.track_filename = track_filename
        self.track_modified = False

        self.load_ui()
        self.connect_menubar_to_slots()
        self.connect_signals_to_slots()

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
        self.image_panel = imagepanel.ImagePanel(self.ui)
        self.zoom_panel = zoompanel.ZoomPanel(self.ui)

    def connect_menubar_to_slots (self):
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_tracks.triggered.connect(self.slot_load_tracks)
        self.ui.action_save_tracks.triggered.connect(self.slot_save_tracks)
        self.ui.action_save_tracks_as.triggered.connect(self.slot_save_tracks_as)
        self.ui.action_zoom_in.triggered.connect(self.slot_zoom_in)
        self.ui.action_zoom_out.triggered.connect(self.slot_zoom_out)
        self.ui.action_zoom_reset.triggered.connect(self.slot_zoom_reset)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_quick_help.triggered.connect(self.slot_quick_help)

    def connect_signals_to_slots (self):
        self.image_panel.scene.mousePressEvent = self.slot_mouse_clicked
        self.ui.slider_time.valueChanged.connect(self.slot_slider_moved)
        self.ui.slider_zstack.valueChanged.connect(self.slot_slider_moved)
        self.ui.button_zoom_in.clicked.connect(self.slot_zoom_in)
        self.ui.button_zoom_out.clicked.connect(self.slot_zoom_out)
        self.ui.button_zoom_reset.clicked.connect(self.slot_zoom_reset)

    def load_image (self):
        try:
            self.image_stack = stack.Stack(self.image_filename)
            self.image_panel.init_sliders(self.image_stack)
            self.image_panel.update_image_scene(self.image_stack)
            self.update_window_title()
        except FileNotFoundError:
            self.show_message(title = "Image loading error", message = "Failed to load image: {0}".format(self.image_filename))

    def load_tracks (self):
        pass

    def save_tracks (self):
        ## save here
        self.track_modified = False

    def update_window_title (self):
        self.setWindowTitle(self.app_name + " - " + Path(self.image_filename).name)

    def update_image_view (self):
        self.image_panel.update_image_scene(self.image_stack, self.zoom_panel.zoom_ratio)

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

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

    def slot_mouse_clicked (self, event):
        print(event.scenePos())

    def slot_slider_moved (self):
        self.update_image_view()

    def slot_zoom_in (self):
        self.zoom_panel.zoom_in()
        self.update_image_view()

    def slot_zoom_out (self):
        self.zoom_panel.zoom_out()
        self.update_image_view()

    def slot_zoom_reset (self):
        self.zoom_panel.zoom_reset()
        self.update_image_view()

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


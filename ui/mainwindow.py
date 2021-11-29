#!/usr/bin/env python

import sys
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QFile, QTimer, Qt
from PySide6.QtUiTools import QUiLoader
from ui import imagepanel, zoompanel, lutpanel
from image import stack

class MainWindow (QMainWindow):
    def __init__ (self, image_filename = None, record_filename = None):
        super().__init__()
        self.app_name = "PyTrace"

        self.image_filename = image_filename
        self.record_filename = record_filename
        self.record_modified = False

        self.load_ui()

        if self.image_filename is not None:
            self.load_image()
        if self.record_modified is not None:
            self.load_records()

        self.connect_menubar_to_slots()
        self.connect_signals_to_slots()

    def load_ui (self):
        file = QFile("ui/mainwindow.ui")
        file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui)

        self.lut_panel = lutpanel.LutPanel(self.ui)
        self.zoom_panel = zoompanel.ZoomPanel(self.ui)
        self.image_panel = imagepanel.ImagePanel(self.ui)
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(100)

    def connect_menubar_to_slots (self):
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_records.triggered.connect(self.slot_load_records)
        self.ui.action_save_records.triggered.connect(self.slot_save_records)
        self.ui.action_save_records_as.triggered.connect(self.slot_save_records_as)
        self.ui.action_zoom_in.triggered.connect(self.slot_zoomed_in)
        self.ui.action_zoom_out.triggered.connect(self.slot_zoomed_out)
        self.ui.action_zoom_reset.triggered.connect(self.slot_zoom_reset)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_quick_help.triggered.connect(self.slot_quick_help)

    def connect_signals_to_slots (self):
        # scene
        self.image_panel.scene.mousePressEvent = self.slot_scene_mouse_clicked
        self.image_panel.scene.keyPressEvent = self.slot_scene_key_pressed
        self.image_panel.scene.keyReleaseEvent = self.slot_scene_key_released

        # time and zstack
        self.ui.slider_time.valueChanged.connect(self.slot_image_index_changed)
        self.ui.slider_zstack.valueChanged.connect(self.slot_image_index_changed)
        self.ui.button_play.clicked.connect(self.slot_slideshow_switched)
        self.ui.spin_fps.valueChanged.connect(self.slot_slideshow_changed)
        self.play_timer.timeout.connect(self.slot_slideshow_timeout)

        # zooming
        self.ui.button_zoom_in.clicked.connect(self.slot_zoomed_in)
        self.ui.button_zoom_out.clicked.connect(self.slot_zoomed_out)
        self.ui.button_zoom_reset.clicked.connect(self.slot_zoom_reset)

        # lut
        self.ui.combo_channel.currentIndexChanged.connect(self.slot_channel_changed)
        self.ui.check_composite.stateChanged.connect(self.slot_channel_changed)
        self.ui.check_color_always.stateChanged.connect(self.slot_channel_changed)
        self.ui.check_invert_lut.stateChanged.connect(self.slot_lut_changed)
        self.ui.combo_lut.currentIndexChanged.connect(self.slot_lut_changed)
        self.ui.combo_bits.currentIndexChanged.connect(self.slot_bits_changed)
        self.ui.check_auto_lut.stateChanged.connect(self.slot_auto_lut_changed)
        self.ui.dspin_auto_cutoff.valueChanged.connect(self.slot_auto_lut_changed)
        self.ui.slider_cutoff_lower.valueChanged.connect(self.slot_lut_lower_changed)
        self.ui.slider_cutoff_upper.valueChanged.connect(self.slot_lut_upper_changed)
        self.ui.button_reset_lut.clicked.connect(self.slot_reset_lut)

    def load_image (self):
        try:
            self.image_stack = stack.Stack(self.image_filename)
            self.image_panel.init_widgets(self.image_stack)
            self.zoom_panel.zoom_reset()
            self.lut_panel.init_widgets(self.image_stack)
            self.update_image_view()
            self.update_window_title()
        except FileNotFoundError:
            self.show_message(title = "Image loading error", message = "Failed to load image: {0}".format(self.image_filename))

    def load_records (self):
        pass

    def save_records (self):
        ## save here
        self.records_modified = False

    def update_window_title (self):
        self.setWindowTitle(self.app_name + " - " + Path(self.image_filename).name)

    def update_image_view (self):
        self.image_panel.update_image_scene(self.image_stack, lut_list = self.lut_panel.lut_list, \
                                            channel = self.lut_panel.current_channel(), composite = self.lut_panel.is_composite(), \
                                            color_always = self.lut_panel.color_always(), zoom_ratio = self.zoom_panel.zoom_ratio)
        self.lut_panel.update_lut_view(self.image_panel.current_image(self.image_stack, self.lut_panel.current_channel()))

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
        image_filename = dialog.selectedFiles()[0]
        new_window = MainWindow(image_filename = image_filename)
        new_window.show()

    def slot_load_records (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a record to load.")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["JSON file (*.json)", "Any (*.*)"])
        dialog.setViewMode(QFileDialog.List)
        dialog.exec()
        # load image here
        print(dialog.selectedFiles())

    def slot_save_records (self):
        if self.records_filename is None:
            self.slot_save_records_as()
        else:
            self.save_records()

    def slot_save_records_as (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a filename to save records.")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(["JSON file (*.json)", "Any (*.*)"])
        dialog.setViewMode(QFileDialog.List)
        result = dialog.exec()
        if result == QFileDialog.Save:
            print(dialog.selectedFiles())
            self.save_records()

    def slot_quick_help (self):
        self.show_message(title = "Quick help", message = "Currently nothing to show...")

    def slot_about_this (self):
        self.show_message(title = "About This",
                          message = "Object tracking system for time-lapse 2D/3D images.\n" +
                                    "Copyright 2021 by Takushi Miyoshi (NIH/NIDCD).")

    def slot_scene_mouse_clicked (self, event):
        print(event.scenePos())

    def slot_scene_key_pressed (self, event):
        self.ui.gview_image.setCursor(Qt.CrossCursor)

    def slot_scene_key_released (self, event):
        self.ui.gview_image.setCursor(Qt.ArrowCursor)

    def slot_image_index_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack, self.lut_panel.current_channel()))
        self.update_image_view()

    def slot_channel_changed (self):
        self.lut_panel.update_channel_widgets()
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack, self.lut_panel.current_channel()))
        self.update_image_view()

    def slot_lut_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack, self.lut_panel.current_channel()))
        else:
            self.lut_panel.update_current_lut()
        self.update_image_view()

    def slot_bits_changed (self):
        self.lut_panel.update_current_bits()
        self.update_image_view()

    def slot_lut_lower_changed (self):
        self.lut_panel.adjust_slider_upper()
        self.lut_panel.update_current_lut()
        self.update_image_view()

    def slot_lut_upper_changed (self):
        self.lut_panel.adjust_slider_lower()
        self.lut_panel.update_current_lut()
        self.update_image_view()
    
    def slot_auto_lut_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack, self.lut_panel.current_channel()))
            self.update_image_view()

    def slot_reset_lut (self):
        self.lut_panel.reset_current_lut()
        self.update_image_view()

    def slot_zoomed_in (self):
        self.zoom_panel.zoom_in()
        self.update_image_view()

    def slot_zoomed_out (self):
        self.zoom_panel.zoom_out()
        self.update_image_view()

    def slot_zoom_reset (self):
        self.zoom_panel.zoom_reset()
        self.update_image_view()

    def slot_slideshow_switched (self):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.ui.button_play.setText("Play")
        else:
            self.play_timer.start()
            self.ui.button_play.setText("Stop")

    def slot_slideshow_changed (self):
        self.play_timer.setInterval(1000 / self.ui.spin_fps.value())

    def slot_slideshow_timeout (self):
        self.ui.slider_time.setValue((self.ui.slider_time.value() + 1) % self.image_stack.t_count)

    def showEvent (self, event):
        self.update_image_view()

    def closeEvent (self, event):
        if self.record_modified:
            mbox = QMessageBox()
            mbox.setWindowTitle("Save Records?")
            mbox.setText("Record modified. Save?")
            mbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mbox.setDefaultButton(QMessageBox.Cancel)
            result = mbox.exec()
            if result == QMessageBox.Cancel:
                event.ignore()
            elif result == QMessageBox.Discard:
                event.accept()
            else:
                if self.record_filename is None:
                    self.slot_save_records_as()
                else:
                    self.slot_save_records()
                if self.record_modified:
                    event.ignore()


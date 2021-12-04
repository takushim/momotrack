#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QTextEdit
from plugin.base import PluginBase

plugin_name = 'Particle Tracking'
class_name = 'SPT'
priority = 10
record_suffix = '_track.json'

class SPT (PluginBase):
    def __init__ (self):
        super().__init__()

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.text_message = QTextEdit()
        self.vlayout.addWidget(self.check_hide_tracks)
        self.vlayout.addWidget(self.text_message)

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_hide_tracks)

    def slot_hide_tracks (self):
        self.signal_request_image_update.emit()

    def generate_scene_items (self):
        if self.check_hide_tracks.isChecked() == False:
            pass

    def key_pressed (self, event, ui):
        if event.key() == Qt.Key_Control:
            ui.setCursor(Qt.CrossCursor)

    def key_released (self, event, ui):
        if event.key() == Qt.Key_Control:
            ui.setCursor(Qt.ArrowCursor)

    def override_mouse_click (self, event, ui):
        print("MOUSE")


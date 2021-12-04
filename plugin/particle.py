#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QTextEdit, QGraphicsEllipseItem
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

    def scene_items (self):
        scene_items = []
        if self.check_hide_tracks.isChecked() == False:
            for index in range(100):
                pos = 256 * np.random.random(2)
                item = QGraphicsEllipseItem(pos[0] - 2, pos[1] - 2, pos[0] + 2, pos[1] + 2)
                scene_items.append(item)
        return scene_items        

    def key_pressed (self, event, ui):
        if event.key() == Qt.Key_Control:
            ui.setCursor(Qt.CrossCursor)

    def key_released (self, event, ui):
        if event.key() == Qt.Key_Control:
            ui.setCursor(Qt.ArrowCursor)

    def mouse_clicked (self, event, ui):
        print("MOUSE")


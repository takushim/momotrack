#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QGraphicsEllipseItem, QSizePolicy
from PySide6.QtGui import QPen
from plugin.base import PluginBase

plugin_name = 'Particle Tracking'
class_name = 'SPT'
priority = 10
record_suffix = '_track.json'

class SPT (PluginBase):
    def __init__ (self):
        super().__init__()
        self.spot_list = []
        self.spot_radius = 2

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.text_message = QLabel()
        self.text_message.setText("Ctrl + click to start tracking.")
        self.vlayout.addWidget(self.check_hide_tracks)
        self.vlayout.addWidget(self.text_message)

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_hide_tracks)

    def slot_hide_tracks (self):
        self.signal_update_scene.emit()

    def scene_items (self):
        scene_items = []
        if self.check_hide_tracks.isChecked() == False:
            for index in range(100):
                pos = 256 * np.random.random(2)
                item = QGraphicsEllipseItem(pos[0] - 2, pos[1] - 2, 2, 2)
                item.setPen(QPen(Qt.white))
                #scene_items.append(item)
        return scene_items

    def key_pressed (self, event, image_index, stack):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)

    def key_released (self, event, image_index, stack):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def mouse_clicked (self, event, image_index, stack):
        if event.modifiers() == Qt.CTRL:
            self.add_spot(event.scenePos(), parent = None)
        else:
            print(event)
            self.select_spot(event.scenePos())

    def add_spot (self, pos, parent = None):
        print(pos)
    
    def select_spot (self, pos):
        print(pos)

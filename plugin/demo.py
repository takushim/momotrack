#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QTextEdit, QGraphicsEllipseItem
from PySide6.QtGui import QPen, QColor
from plugin.base import PluginBase

plugin_name = 'Demo'
class_name = 'Demo'
priority = 100
record_suffix = '_demo.json'

class Demo (PluginBase):
    def __init__ (self):
        super().__init__()
        self.diameter = 4
        self.color_list = [Qt.white, Qt.red, Qt.green, Qt.blue, Qt.magenta, Qt.yellow, Qt.cyan]

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.button_demo = QPushButton("Demo Button")
        self.text_message = QTextEdit()
        self.vlayout.addWidget(self.button_demo)
        self.vlayout.addWidget(self.text_message)

    def connect_signals (self):
        self.button_demo.clicked.connect(self.slot_demo_button)

    def slot_demo_button (self):
        self.signal_update_image.emit()

    def scene_items (self):
        scene_items = []
        for index in range(100):
            pos = 256 * np.random.random(2)
            item = QGraphicsEllipseItem(pos[0] - self.diameter, pos[1] - self.diameter, self.diameter, self.diameter)
            item.setPen(QPen(self.color_list[index % len(self.color_list)]))
            scene_items.append(item)
        return scene_items

    def key_pressed (self, event):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)

    def key_released (self, event):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def mouse_clicked (self, event):
        self.text_message.setText("Mouse clicked: ({0}, {1})".format(event.scenePos().x(), event.scenePos().y()))

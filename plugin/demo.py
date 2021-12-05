#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsEllipseItem
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
        self.item_list = []

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.button_demo = QPushButton("Demo Button")
        self.text_message = QLabel()
        self.vlayout.addWidget(self.button_demo)
        self.vlayout.addWidget(self.text_message)

    def connect_signals (self):
        self.button_demo.clicked.connect(self.slot_demo_button)

    def slot_demo_button (self):
        self.text_message.setText("Button clicked.")

    def list_scene_items (self, tcz_index):
        return self.item_list

    def key_pressed (self, event, stack, tcz_index):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)

    def key_released (self, event, stack, tcz_index):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def mouse_clicked (self, event, stack, tcz_index):
        self.text_message.setText("Mouse clicked: ({0:.2f}, {1:.2f})".format(event.scenePos().x(), event.scenePos().y()))
        self.item_list = []
        for index in range(100):
            x = stack.width * np.random.random(1)
            y = stack.height * np.random.random(1)
            item = QGraphicsEllipseItem(x - self.diameter, y - self.diameter, self.diameter, self.diameter)
            item.setPen(QPen(self.color_list[index % len(self.color_list)]))
            self.item_list.append(item)
        self.signal_update_scene.emit()

    def help_message (self):
        return "Demo class for plugin."

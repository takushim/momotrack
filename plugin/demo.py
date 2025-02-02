#!/usr/bin/env python

import textwrap
import numpy as np
from logging import getLogger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsEllipseItem
from PySide6.QtGui import QPen
from plugin.base import PluginBase

logger = getLogger(__name__)

plugin_name = 'Demo'
class_name = 'Demo'
priority = 100

class Demo (PluginBase):
    def __init__ (self):
        super().__init__()
        self.diameter = 4
        self.color_list = [Qt.white, Qt.red, Qt.green, Qt.blue, Qt.magenta, Qt.yellow, Qt.cyan]
        self.item_list = []
        self.record_suffix = '_demo.json'

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.button_demo = QPushButton("Demo Button")
        self.text_message = QLabel()
        self.text_message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.vlayout.addWidget(self.button_demo)
        self.vlayout.addWidget(self.text_message)

    def connect_signals_to_slots (self):
        self.button_demo.clicked.connect(self.slot_demo_button)

    def slot_demo_button (self):
        text = "Button clicked."
        logger.info(text)
        self.text_message.setText(text)
        self.signal_update_image_view.emit()

    def list_scene_items (self, stack, tcz_index):
        self.update_spots(stack.width, stack.height)
        return self.item_list

    def key_pressed (self, event, stack, tcz_index):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)

    def key_released (self, event, stack, tcz_index):
        if event.key() == Qt.Key_Control:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def mouse_pressed (self, event, stack, tcz_index):
        text = "Mouse pressed: ({0:.2f}, {1:.2f})".format(event.scenePos().x(), event.scenePos().y())
        logger.info(text)
        self.text_message.setText(text)
        self.update_spots(stack.width, stack.height)
        self.signal_update_image_view.emit()

    def update_spots (self, width, height):
        self.item_list = []
        for index in range(100):
            x = width * np.random.random(1)
            y = height * np.random.random(1)
            d = self.diameter * np.random.random(1)
            item = QGraphicsEllipseItem(x - d, y - d, d, d)
            item.setPen(QPen(self.color_list[index % len(self.color_list)]))
            self.item_list.append(item)

    def help_message (self):
        message = textwrap.dedent('''\
        <b>Demonstration of the plugin system</b><br><br>
        This plugin draws multiple spots on the image.
        Click or press "Demo Button" to update spots.
        Press Ctrl to see the mouse cursor change.
        ''')
        return message

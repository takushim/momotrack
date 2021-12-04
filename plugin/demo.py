#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtWidgets import QPushButton, QTextEdit
from plugin.base import PluginBase

plugin_name = 'Demo'
class_name = 'Demo'
priority = 100
record_suffix = '_demo.json'

class Demo (PluginBase):
    def __init__ (self):
        super().__init__()

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.button_demo = QPushButton("Demo Button")
        self.text_message = QTextEdit()
        self.vlayout.addWidget(self.button_demo)
        self.vlayout.addWidget(self.text_message)

    def connect_signals (self):
        self.button_demo.clicked.connect(self.slot_demo_button)

    def slot_demo_button (self):
        print("Demo")

#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QCheckBox, QTextEdit

priority = -1
plugin_name = 'Base class'
class_name = 'PluginBase'
record_suffix = '_record.json'

class PluginBase (QObject):
    signal_request_image_update = Signal()

    def __init__ (self):
        super().__init__()

    def init_widgets (self, vlayout):
        pass

    def connect_signals (self):
        pass

    def generate_scene_items (self):
        pass

    def key_pressed (self, event, ui):
        pass

    def key_released (self, event, ui):
        pass

    def mouse_clicked (self, event, ui):
        pass

    def load_records (self, filename):
        pass

    def save_records (self, filename):
        pass

    def clear_records (self):
        pass

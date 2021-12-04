#!/usr/bin/env python

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor

priority = -1
plugin_name = 'Base class'
class_name = 'PluginBase'
record_suffix = '_record.json'

class PluginBase (QObject):
    signal_update_scene = Signal()
    signal_update_lut = Signal()
    signal_reset_panels = Signal()
    signal_update_mouse_cursor = Signal(QCursor)

    def __init__ (self):
        super().__init__()

    def init_widgets (self, vlayout):
        pass

    def connect_signals (self):
        pass

    def scene_items (self):
        pass

    def key_pressed (self, event, image_index, stack):
        pass

    def key_released (self, event, image_index, stack):
        pass

    def mouse_clicked (self, event, image_index, stack):
        pass

    def load_records (self, filename):
        pass

    def save_records (self, filename):
        pass

    def clear_records (self):
        pass

#!/usr/bin/env python

import re
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor

priority = -1
plugin_name = 'Base class'
class_name = 'PluginBase'
record_suffix = '_record.json'
default_filename = 'default' + record_suffix

class PluginBase (QObject):
    signal_update_scene = Signal()
    signal_update_lut = Signal()
    signal_reset_panels = Signal()
    signal_update_mouse_cursor = Signal(QCursor)

    def __init__ (self):
        super().__init__()
        self.records_modified = False

    def init_widgets (self, vlayout):
        pass

    def connect_signals (self):
        pass

    def list_scene_items (self, tcz_index):
        pass

    def key_pressed (self, event, stack, tcz_index):
        pass

    def key_released (self, event, stack, tcz_index):
        pass

    def mouse_clicked (self, event, stack, tcz_index):
        pass

    def load_records (self, records_filename):
        pass

    def save_records (self, records_filename, image_filename):
        pass

    def clear_records (self):
        pass

    def suggest_filename (self, image_filename):
        if image_filename is None:
            return default_filename

        name = Path(image_filename).stem
        name = re.sub('\.ome$', '', name, flags=re.IGNORECASE)
        return name + record_suffix

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        return "Base class to implement plugins. Do not use."

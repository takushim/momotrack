#!/usr/bin/env python

import re, time, json
from pathlib import Path
from numpyencoder import NumpyEncoder
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor

priority = -1
plugin_name = 'Base class'
class_name = 'PluginBase'

class PluginBase (QObject):
    signal_update_scene = Signal()
    signal_update_lut = Signal()
    signal_reset_panels = Signal()
    signal_update_mouse_cursor = Signal(QCursor)
    signal_move_by_tczindex = Signal(int, int, int)

    def __init__ (self):
        super().__init__()
        self.records_modified = False
        self.record_suffix = '_record.json'
        self.default_stem = 'default'
        self.file_types = {"JSON text": ["*.json"]}

    def check_records (self, plugin_name, records_filename):
        with open(records_filename, 'r') as f:
            json_dict = json.load(f)

        if 'summary' not in json_dict:
            return False

        summary = json_dict.get('summary', None)
        if summary.get('plugin_name', '') != plugin_name:
            return False

        return True

    def load_records (self, records_filename):
        with open(records_filename, 'r') as f:
            self.json_dict = json.load(f)

        self.image_settings = self.json_dict.get('image_settings', {})

    def save_records (self, records_filename, image_settings = {}):
        summary = {'plugin_name': self.plugin_name, \
                   'last_update': time.strftime("%a %d %b %H:%M:%S %Z %Y")}

        json_dict = {}
        json_dict['summary'] = summary
        json_dict['image_settings'] = image_settings
        self.json_dict = json_dict | self.json_dict

        with open(records_filename, 'w') as f:
            json.dump(self.json_dict, f, ensure_ascii = False, indent = 4, sort_keys = False, \
                      separators = (',', ': '), cls = NumpyEncoder)

    def clear_records (self):
        pass

    def suggest_filename (self, image_filename):
        if image_filename is None:
            return self.default_filename + self.record_suffix

        name = Path(image_filename).stem
        name = re.sub('\.ome$', '', name, flags=re.IGNORECASE)
        return name + self.record_suffix

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        return "Base class to implement plugins. Do not use."

    def init_widgets (self, vlayout):
        pass

    def update_stack_info (self, stack):
        pass

    def connect_signals (self):
        pass

    def list_scene_items (self, stack, tcz_index):
        pass

    def key_pressed (self, event, stack, tcz_index):
        pass

    def key_released (self, event, stack, tcz_index):
        pass

    def mouse_clicked (self, event, stack, tcz_index):
        pass

    def mouse_moved (self, event, stack, tcz_index):
        pass

    def mouse_released (self, event, stack, tcz_index):
        pass


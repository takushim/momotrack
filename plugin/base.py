#!/usr/bin/env python

import re, json, textwrap
from datetime import datetime
from pathlib import Path
from numpyencoder import NumpyEncoder
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor

priority = -1
plugin_name = 'Base class'
class_name = 'PluginBase'

class PluginException(Exception):
    def __init__ (self, message = "Unknown exception"):
        self.message = message

    def __str__ (self):
        return "Plugin: {0}".format(self.message)

class PluginBase (QObject):
    signal_update_image_view = Signal()
    signal_reset_panels = Signal()
    signal_update_mouse_cursor = Signal(QCursor)
    signal_move_by_tczindex = Signal(int, int, int)
    signal_focus_graphics_view = Signal()

    def __init__ (self):
        super().__init__()
        self.records_modified = False
        self.record_suffix = '_record.json'
        self.default_stem = 'default'
        self.file_types = {"JSON text": ["*.json"]}

    def load_records (self, records_filename):
        try:
            with open(records_filename, 'r') as f:
                self.records_dict = json.load(f)
        except:
            raise PluginException(f"Record File unable to load: {records_filename}")

        plugin_name = self.records_dict.get('summary', {}).get('plugin_name', '')
        if plugin_name != self.plugin_name:
            raise PluginException(f"The records were created by different plugin: {plugin_name}")

    def save_records (self, records_filename, settings = {}):
        summary = {'plugin_name': self.plugin_name, \
                   'last_update': datetime.now().astimezone().isoformat()}

        self.records_dict = {'summary': summary} | settings | self.records_dict

        try:
            with open(records_filename, 'w') as f:
                json.dump(self.records_dict, f, ensure_ascii = False, indent = 4, sort_keys = False, \
                        separators = (',', ': '), cls = NumpyEncoder)
        except:
            raise PluginException(f"Record File unable to save: {records_filename}")

    def clear_records (self):
        self.records_dict = {}

    def suggest_filename (self, image_filename):
        if image_filename is None:
            return self.default_filename + self.record_suffix

        name = Path(image_filename).stem
        name = re.sub(r'\.ome$', '', name, flags=re.IGNORECASE)
        return name + self.record_suffix

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        message = textwrap.dedent('''\
        <b>Base class for plugins</b><br><br>
        Loaded when no plugins are working.
        Make a new class inheriting this class and
        do not use this class directly.
        ''')

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

    def mouse_pressed (self, event, stack, tcz_index):
        pass

    def mouse_moved (self, event, stack, tcz_index):
        pass

    def mouse_released (self, event, stack, tcz_index):
        pass

    def focus_recovered (self):
        pass

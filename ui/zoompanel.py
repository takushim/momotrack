#!/usr/bin/env python

import numpy as np
from PySide6.QtCore import QObject, Signal

class ZoomPanel (QObject):
    signal_zoom_ratio_changed = Signal(int)

    def __init__ (self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui
        self.init_widgets()

    def init_widgets (self):
        self.zoom_ratio = 100
        self.zoom_limits = [25, 800]
        self.zoom_delta = 25

    def connect_signals_to_slots (self):
        self.ui.button_zoom_in.clicked.connect(self.slot_zoomed_in)
        self.ui.button_zoom_out.clicked.connect(self.slot_zoomed_out)
        self.ui.button_zoom_reset.clicked.connect(self.slot_zoom_reset)

    def update_zoom_label (self):
        status = "Current zoom: {0}%".format(self.zoom_ratio)
        self.ui.label_zoom_status.setText(status)

    def set_zoom (self, ratio):
        if ratio in range(self.zoom_limits[0], self.zoom_limits[1] + self.zoom_delta, self.zoom_delta):
            self.zoom_ratio = ratio
            self.update_zoom_label()
            self.signal_zoom_ratio_changed.emit(self.zoom_ratio)

    def zoom_best (self, image_size, scene_size):
        ratio = np.min((np.array(scene_size).astype(float) / np.array(image_size).astype(float)) * 100.0)
        current_zoom = self.zoom_limits[0]
        next_zoom = current_zoom + self.zoom_delta
        while next_zoom <= min(self.zoom_limits[1], ratio):
            current_zoom = next_zoom
            next_zoom = current_zoom + self.zoom_delta
        self.zoom_ratio = current_zoom
        self.update_zoom_label()
        self.signal_zoom_ratio_changed.emit(self.zoom_ratio)

    def slot_zoomed_in (self):
        self.zoom_ratio = min(self.zoom_ratio + self.zoom_delta, self.zoom_limits[1])
        self.update_zoom_label()
        self.signal_zoom_ratio_changed.emit(self.zoom_ratio)

    def slot_zoomed_out (self):
        self.zoom_ratio = max(self.zoom_ratio - self.zoom_delta, self.zoom_limits[0])
        self.update_zoom_label()
        self.signal_zoom_ratio_changed.emit(self.zoom_ratio)

    def slot_zoom_reset (self):
        self.zoom_ratio = 100
        self.update_zoom_label()
        self.signal_zoom_ratio_changed.emit(self.zoom_ratio)


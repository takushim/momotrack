#!/usr/bin/env python

import numpy as np

class ZoomPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.zoom_ratio = 100
        self.zoom_limits = [25, 800]
        self.zoom_delta = 25

    def update_zoom_label (self):
        status = "Current zoom: {0}%".format(self.zoom_ratio)
        self.ui.label_zoom_status.setText(status)

    def zoom_in (self):
        self.zoom_ratio = min(self.zoom_ratio + self.zoom_delta, self.zoom_limits[1])
        self.update_zoom_label()

    def zoom_out (self):
        self.zoom_ratio = max(self.zoom_ratio - self.zoom_delta, self.zoom_limits[0])
        self.update_zoom_label()

    def zoom_reset (self):
        self.zoom_ratio = 100
        self.update_zoom_label()

    def zoom_best (self, image_size, scene_size):
        ratio = np.min((np.array(scene_size).astype(float) / np.array(image_size).astype(float)) * 100.0)
        current_zoom = self.zoom_limits[0]
        next_zoom = current_zoom + self.zoom_delta
        while next_zoom <= min(self.zoom_limits[1], ratio):
            current_zoom = next_zoom
            next_zoom = current_zoom + self.zoom_delta
        self.zoom_ratio = current_zoom
        self.update_zoom_label()

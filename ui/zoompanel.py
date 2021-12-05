#!/usr/bin/env python

zoom_limits = [25, 400]
zoom_delta = 25

class ZoomPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.zoom_ratio = 100

    def update_zoom_label (self):
        status = "Current zoom: {0}%".format(self.zoom_ratio)
        self.ui.label_zoom_status.setText(status)

    def zoom_in (self):
        self.zoom_ratio = min(self.zoom_ratio + zoom_delta, zoom_limits[1])
        self.update_zoom_label()

    def zoom_out (self):
        self.zoom_ratio = max(self.zoom_ratio - zoom_delta, zoom_limits[0])
        self.update_zoom_label()

    def zoom_reset (self):
        self.zoom_ratio = 100
        self.update_zoom_label()



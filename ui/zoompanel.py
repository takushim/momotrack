#!/usr/bin/env python

import sys
import numpy as np

zoom_ratios = [25, 50, 75, 100, 150, 200, 300, 400]

class ZoomPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.zoom_ratio = 100

    def update_zoom_label (self):
        status = "Current zoom: {0}%".format(self.zoom_ratio)
        self.ui.label_zoom_status.setText(status)

    def zoom_in (self):
        self.zoom_ratio = zoom_ratios[min(zoom_ratios.index(self.zoom_ratio) + 1, len(zoom_ratios) - 1)]
        self.update_zoom_label()
        print(self.zoom_ratio)

    def zoom_out (self):
        self.zoom_ratio = zoom_ratios[max(zoom_ratios.index(self.zoom_ratio) - 1, 0)]
        self.update_zoom_label()

    def zoom_reset (self):
        self.zoom_ratio = 100
        self.update_zoom_label()



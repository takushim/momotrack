#!/usr/bin/env python

import sys
import numpy as np

class PluginPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.zoom_ratio = 100

    def update_title (self, name):
        self.ui.label_plugin.setText("Plugin: {0}".format(name))


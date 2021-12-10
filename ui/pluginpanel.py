#!/usr/bin/env python

from pathlib import Path
from PySide6.QtWidgets import QSizePolicy, QLayout

class PluginPanel:
    def __init__ (self, ui):
        self.ui = ui

    def update_title (self, name):
        self.ui.label_plugin.setText("Plugin: {0}".format(name))

    def update_filename (self, filename):
        if filename is None:
            filename = "(None)"
        self.ui.label_records_filename.setText("Current file: {0}".format(Path(filename).name))

    def update_widgets (self, plugin_class):
        self.recurse_plugin_widgets(self.ui.vlayout_plugin, lambda x: x.deleteLater(), lambda x: x.deleteLater())

        self.plugin_class = plugin_class
        self.plugin_class.init_widgets(self.ui.vlayout_plugin)
        self.plugin_class.connect_signals()

        self.recurse_plugin_widgets(self.ui.vlayout_plugin, \
                                    lambda x: x.setSizeConstraint(QLayout.SetMinimumSize), \
                                    lambda x: x.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

    def recurse_plugin_widgets (self, object, func_layout, func_widget):
        for index in reversed(range(object.count())):
            if object.itemAt(index).widget() is None:
                self.recurse_plugin_widgets(object.itemAt(index).layout(), func_layout, func_widget)
                func_layout(object.itemAt(index).layout())
            else:
                func_widget(object.itemAt(index).widget())


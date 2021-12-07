#!/usr/bin/env python

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QLayout

class PluginPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.module = None

    def update_title (self, name):
        self.ui.label_plugin.setText("Plugin: {0}".format(name))

    def update_widgets (self, plugin_class):
        self.delete_plugin_widgets(self.ui.vlayout_plugin)

        self.plugin_class = plugin_class
        self.plugin_class.init_widgets(self.ui.vlayout_plugin)
        self.plugin_class.connect_signals()

        self.set_policy_of_plugin_widgets(self.ui.vlayout_plugin)

    def delete_plugin_widgets (self, layout):
        for index in reversed(range(layout.count())):
            if layout.itemAt(index).widget() is None:
                self.delete_plugin_widgets(layout.itemAt(index).layout())
            else:
                layout.itemAt(index).widget().deleteLater()

    def set_policy_of_plugin_widgets (self, layout):
        for index in reversed(range(layout.count())):
            if layout.itemAt(index).widget() is None:
                layout.itemAt(index).layout().setSizeConstraint(QLayout.SetMinimumSize)
                self.set_policy_of_plugin_widgets(layout.itemAt(index).layout())
            else:
                layout.itemAt(index).widget().setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)


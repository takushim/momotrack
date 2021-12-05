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
        for index in reversed(range(self.ui.vlayout_plugin.count())):
            if self.ui.vlayout_plugin.itemAt(index).widget() is None:
                self.ui.vlayout_plugin.itemAt(index).layout().deleteLater()
            else:
                self.ui.vlayout_plugin.itemAt(index).widget().deleteLater()

        self.plugin_class = plugin_class
        self.plugin_class.init_widgets(self.ui.vlayout_plugin)
        self.plugin_class.connect_signals()

        for index in range(self.ui.vlayout_plugin.count()):
            if self.ui.vlayout_plugin.itemAt(index).widget() is None:
                self.ui.vlayout_plugin.itemAt(index).layout().setSizeConstraint(QLayout.SetMinimumSize)
            else:
                self.ui.vlayout_plugin.itemAt(index).widget().setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                self.ui.vlayout_plugin.itemAt(index).widget().setFocusPolicy(Qt.NoFocus)

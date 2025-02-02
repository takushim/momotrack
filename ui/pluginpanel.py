#!/usr/bin/env python

from pathlib import Path
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QSizePolicy, QLayout

class PluginPanel (QObject):
    signal_plugin_changed = Signal()

    def __init__ (self, ui):
        self.ui = ui
        self.update_filename(filename = None, modified = False)

    def update_title (self, name):
        self.ui.label_plugin.setText("Plugin: {0}".format(name))

    def update_filename (self, filename, modified):
        flag = '*' if modified else ''
        if filename is None:
            text = "File: {0}(None)".format(flag)
        else:
            text = "File: {0}{1}".format(flag, Path(filename).name)

        self.ui.label_records_filename.setToolTip(text)

        fontmetrics = QFontMetrics(self.ui.label_records_filename.font())
        text = fontmetrics.elidedText(text, Qt.TextElideMode.ElideRight, self.ui.label_records_filename.width())
        self.ui.label_records_filename.setText(text)

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


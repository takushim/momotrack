#!/usr/bin/env python

from pathlib import Path
from importlib import import_module
from PySide6.QtGui import QAction, QActionGroup, QFontMetrics, QCursor
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QSizePolicy, QLayout, QMessageBox, QFileDialog

class PluginPanel (QObject):
    # signal from this panel or relayed from plugins
    signal_update_image_view = Signal()

    # signals relayed from plugins to the main window
    signal_update_mouse_cursor = Signal(QCursor)
    signal_select_image_by_tczindex = Signal(int, int, int)
    signal_focus_graphics_view = Signal()
    signal_records_updated = Signal()

    def __init__ (self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui

        self.plugin_module_list = []
        self.plugin_package = 'plugin'
        self.default_plugin = 'base'
        self.current_module = None
        self.current_class = None

        self.load_plugins()
        self.switch_plugin()
        self.connect_signals_to_slots()

    def load_plugins (self):
        plugin_folder = str(Path(__file__).parent.parent.joinpath(self.plugin_package))
        load_failed = []

        self.actgroup_plugin = QActionGroup(self.ui.menu_plugin)

        for module_file in Path(plugin_folder).iterdir():
            if module_file.name.startswith("_"):
                continue
            try:
                module = import_module(name = '{0}.{1}'.format(self.plugin_package, str(module_file.stem)))
                self.plugin_module_list.append(module)
            except ImportError:
                load_failed.append(str(module_file.stem))

        # make sure to load at least one plugin
        self.plugin_module_list = [plugin for plugin in self.plugin_module_list if plugin.priority >= 0]
        if len(self.plugin_module_list) == 0:
            self.plugin_module_list = [import_module(name = '{0}.{1}'.format(self.plugin_package, self.default_plugin))]

        self.plugin_module_list = sorted(self.plugin_module_list, key = lambda x: x.priority)
        for plugin in self.plugin_module_list:
            action = QAction(plugin.plugin_name, self.ui.menu_plugin, checkable = True, checked = False)
            self.ui.menu_plugin.addAction(action)
            self.actgroup_plugin.addAction(action)
        self.actgroup_plugin.setExclusive(True)

        if len(load_failed) > 0:
            self.show_message("Plugin error", "Failed to load: {0}".format(', '.join(load_failed)))

    def connect_signals_to_slots(self):
        self.actgroup_plugin.triggered.connect(self.slot_switch_plugin)

    def find_plugin_module (self, plugin_name):
        return next((x for x in self.plugin_module_list if x.plugin_name == plugin_name), None)

    def switch_plugin (self, plugin_name):
        module = self.find_plugin_module(plugin_name)
        if module is None:
            return
        self.current_module = module

        # disconnect the old class
        self.current_class.clear_records()
        self.current_class.signal_update_image_view.disconnect()
        self.current_class.signal_update_mouse_cursor.disconnect()
        self.current_class.signal_select_image_by_tczindex.disconnect()
        self.current_class.signal_focus_graphics_view.disconnect()
        self.current_class.signal_records_updated.disconnect()

        # connect a new class
        self.current_class = getattr(self.current_module, self.current_module.class_name)()
        self.update_labels()
        self.update_widgets()
        self.current_class.update_stack_info(self.image_panel.image_stack)

        self.current_class.signal_update_image_view.connect(self.slot_update_image_view)
        self.current_class.signal_update_mouse_cursor.connect(self.slot_update_mouse_cursor)
        self.current_class.signal_select_image_by_tczindex.connect(self.slot_select_image_by_tczindex)
        self.current_class.signal_focus_graphics_view.connect(self.slot_focus_graphics_view)
        self.current_class.signal_records_updated.connect(self.slot_records_updated)
        self.update_labels()

        self.signal_update_image_view.emit()

    def update_widgets (self):
        self.recurse_for_widgets(self.ui.vlayout_plugin, lambda x: x.deleteLater(), lambda x: x.deleteLater())

        self.current_class.init_widgets(self.ui.vlayout_plugin)
        self.current_class.connect_signals_to_slots()

        self.recurse_for_widgets(self.ui.vlayout_plugin,
                                 lambda x: x.setSizeConstraint(QLayout.SetMinimumSize),
                                 lambda x: x.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

    def recurse_for_widgets (self, object, func_layout, func_widget):
        for index in reversed(range(object.count())):
            if object.itemAt(index).widget() is None:
                self.recurse_for_widgets(object.itemAt(index).layout(), func_layout, func_widget)
                func_layout(object.itemAt(index).layout())
            else:
                func_widget(object.itemAt(index).widget())

    def update_labels (self):
        fontmetrics = QFontMetrics(self.ui.label_plugin.font())
        text = f"Plugin: {self.current_module.plugin_name}"
        elidedtext = fontmetrics.elidedText(text, Qt.TextElideMode.ElideRight, self.ui.label_plugin.width())
        self.ui.label_plugin.setText(elidedtext)
        if text != elidedtext:
            self.ui.label_plugin.setToolTip(text)

        flag = '*' if self.current_class.is_records_modified() else ''
        if self.current_class.records_filename is None:
            text = f"File: {flag}(None)"
        else:
            text = f"File: {flag}{Path(self.current_class.records_filename).name}"

        fontmetrics = QFontMetrics(self.ui.label_records_filename.font())
        elidedtext = fontmetrics.elidedText(text, Qt.TextElideMode.ElideRight, self.ui.label_records_filename.width())
        self.ui.label_records_filename.setText(elidedtext)
        if text != elidedtext:
            self.ui.label_records_filename.setToolTip(text)

    def load_records (self, records_filename, plugin_name = None):
        try:
            self.current_class.load_records(records_filename)
        except Exception as exception:
            self.show_message(title = "Record loading error", message = str(exception))

        self.update_labels()
        self.signal_update_image_view.emit()

    def save_records (self, records_filename, plugin_name = None, settings = {}):
        if plugin_name is None:
            plugin_module = self.current_module
        else:
            plugin_module = next((x for x in self.plugin_module_list if x.plugin_name == plugin_name), None)

        if plugin_module is None:
            return

        try:
            self.plugin_module.save_records(records_filename, settings = settings)
        except Exception as exception:
            self.show_message(title = "Record saving error", message = str(exception))
            raise
        self.update_labels()

    def clear_records (self):
        self.current_class.clear_records()
        self.update_labels()

    def clear_modified_flag (self):
        if self.plugin_class.is_modified():
            mbox = QMessageBox()
            mbox.setWindowTitle("Save Records?")
            mbox.setText("Record modified. Save?")
            mbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mbox.setDefaultButton(QMessageBox.Cancel)
            result = mbox.exec()
            if result == QMessageBox.Cancel:
                return False
            elif result == QMessageBox.Discard:
                self.plugin_class.clear_records()
                return True
            else:
                self.slot_save_records()
                if self.plugin_class.is_modified():
                    return False

        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())
        return True

    def update_plugin_stack_info (self, stack):
        for plugin in self.plugin_module_list:
            plugin.update_stack_info(stack)

    def notice_focus_recovery (self):
        self.current_class.notice_focus_recovery

    def current_records (self):
        return self.current_class.records_dict

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def slot_switch_plugin (self, action):
        self.switch_plugin(action.text())

    def slot_plugin_help (self):
        self.show_message(title = "Quick help", message = self.plugin_class.help_message())
        self.plugin_class.focus_recovered()
        self.activateWindow()




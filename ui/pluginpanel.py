#!/usr/bin/env python

import json
from pathlib import Path
from importlib import import_module
from logging import getLogger
from PySide6.QtGui import QAction, QActionGroup, QFontMetrics, QCursor
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QSizePolicy, QLayout, QMessageBox

logger = getLogger(__name__)

class PluginPanel (QObject):
    # signal from this panel or relayed from plugins
    signal_update_image_view = Signal()
    signal_restore_image_settings = Signal()

    # signals relayed from plugins to the main window
    signal_update_mouse_cursor = Signal(QCursor)
    signal_select_image_by_tczindex = Signal(int, int, int)
    signal_focus_graphics_view = Signal()

    def __init__ (self, ui, parent = None):
        logger.debug("Plugin panel being intialized.")

        super().__init__(parent)
        self.ui = ui

        self.plugin_instance_dict = {}

        self.plugin_package = 'plugin'
        self.default_plugin = 'base'
        self.plugin_folder = str(Path(__file__).parent.parent.joinpath(self.plugin_package))
        logger.debug(f"Plugin folder {self.plugin_folder}")

        self.default_instance = None
        self.current_instance = None

        self.load_plugins()
        logger.debug(f"Plugins loaded {self.plugin_instance_dict}.")

        plugin_name = list(self.plugin_instance_dict.values())[0].plugin_name
        self.switch_plugin(plugin_name)
        logger.debug(f"Plugin switched to {plugin_name}.")

        self.connect_signals_to_slots()
        logger.debug("Plugin panel signal connected.")

    def load_plugins (self):
        load_failed = []

        self.actgroup_plugin = QActionGroup(self.ui.menu_plugin)

        instance_list = []
        module_name_list = [x.stem for x in Path(self.plugin_folder).iterdir() if not x.name.startswith("_")]
        for module_name in module_name_list:
            try:
                module = import_module(name = '{0}.{1}'.format(self.plugin_package, module_name))
                if module.priority < 0:
                    continue
                instance = getattr(module, module.class_name)()
            except:
                load_failed.append(str(module_name))

            # good module
            instance.priority = module.priority
            instance.plugin_name = module.plugin_name
            instance_list.append(instance)

        # make sure to load at least one plugin
        module = import_module(name = f"{self.plugin_package}.{self.default_plugin}")
        instance = getattr(module, module.class_name)()
        instance.priority = 0
        instance.plugin_name = module.plugin_name
        logger.debug(f"Default plugin loaded: {module}")

        self.default_instance = getattr(module, module.class_name)()
        if len(instance_list) == 0:
            instance_list = [self.default_instance]

        # sort instances by priority values
        logger.debug(f"Initial plugin instance list: {instance_list}")
        instance_list = sorted(instance_list, key = lambda x: x.priority) 
        logger.debug(f"Sorted plugin instance list: {instance_list}")

        # menu
        for instance in instance_list:
            action = QAction(instance.plugin_name, self.ui.menu_plugin, checkable = True, checked = False)
            self.ui.menu_plugin.addAction(action)
            self.actgroup_plugin.addAction(action)
        self.actgroup_plugin.setExclusive(True)

        self.plugin_instance_dict = {x.plugin_name: x for x in instance_list}

        if len(load_failed) > 0:
            self.show_message(f"Plugin error", "Failed to load: {', '.join(load_failed)}")

    def connect_signals_to_slots(self):
        self.actgroup_plugin.triggered.connect(self.slot_switch_plugin)

    def switch_plugin (self, plugin_name = None):
        plugin_name = self.select_plugin_instance(plugin_name).plugin_name
        logger.debug(f"Switching plugin from {self.current_instance} to {plugin_name}.")

        if self.current_instance is not None:
            if plugin_name == self.current_instance.plugin_name:
                return

            # disconnect the old class
            self.current_instance.clear_records()
            self.current_instance.signal_update_image_view.disconnect()
            self.current_instance.signal_update_mouse_cursor.disconnect()
            self.current_instance.signal_select_image_by_tczindex.disconnect()
            self.current_instance.signal_focus_graphics_view.disconnect()
            self.current_instance.signal_records_updated.disconnect()
            logger.debug(f"Signals of the current instance {self.current_instance} disconnected.")

        # connect a new class
        self.current_instance = self.plugin_instance_dict.get(plugin_name, self.default_instance)
        logger.debug(f"New current instance {self.current_instance} set to the variable.")

        self.update_labels()
        logger.debug("Labels updated.")

        self.update_plugin_widgets()
        logger.debug("Plugin widgets updated.")

        self.current_instance.signal_update_image_view.connect(self.slot_update_image_view)
        self.current_instance.signal_update_mouse_cursor.connect(self.slot_update_mouse_cursor)
        self.current_instance.signal_select_image_by_tczindex.connect(self.slot_select_image_by_tczindex)
        self.current_instance.signal_focus_graphics_view.connect(self.slot_focus_graphics_view)
        self.current_instance.signal_records_updated.connect(self.slot_records_updated)
        logger.debug(f"Signals of the new instance {self.current_instance} connected.")

        # update menu
        #plugin_action_list = [x for x in self.actgroup_plugin.actions() if x.text() == self.current_instance.plugin_name]
        #print(plugin_action_list)
        #if len(plugin_action_list) > 0:
        #    self.ui.menu_plugin.blockSignals(True)
        #    self.ui.menu_plugin.setActiveAction(self.actgroup_plugin.setActiveAction.actionAt(plugin_action_list[0]))
        #    self.ui.menu_plugin.blockSignals(False)
        #    logger.debug(f"Plugin menu selected {plugin_action_list[0]}.")

        self.signal_update_image_view.emit()

    def update_plugin_widgets (self):
        self.recurse_for_widgets(self.ui.vlayout_plugin, lambda x: x.deleteLater(), lambda x: x.deleteLater())

        self.current_instance.init_widgets(self.ui.vlayout_plugin)
        self.current_instance.connect_signals_to_slots()

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
        text = f"Plugin: {self.current_instance.plugin_name}"
        elidedtext = fontmetrics.elidedText(text, Qt.TextElideMode.ElideRight, self.ui.label_plugin.width())
        self.ui.label_plugin.setText(elidedtext)
        if text != elidedtext:
            self.ui.label_plugin.setToolTip(text)

        flag = '*' if self.current_instance.is_records_modified() else ''
        if self.current_instance.records_filename is None:
            text = f"File: {flag}(None)"
        else:
            text = f"File: {flag}{Path(self.current_instance.records_filename).name}"

        fontmetrics = QFontMetrics(self.ui.label_records_filename.font())
        elidedtext = fontmetrics.elidedText(text, Qt.TextElideMode.ElideRight, self.ui.label_records_filename.width())
        self.ui.label_records_filename.setText(elidedtext)
        if text != elidedtext:
            self.ui.label_records_filename.setToolTip(text)

    def select_plugin_instance (self, plugin_name = None):
        if plugin_name is None:
            plugin_instance = self.current_instance
        else:
            plugin_instance = self.plugin_instance_dict.get(plugin_name, self.default_instance)

        return plugin_instance

    def load_records (self, records_filename, plugin_name = None):
        try:
            with open(records_filename, 'r') as f:
                records_dict = json.load(f)
        except:
            logger.error(f"Records file cannot be opened for the initial check: {records_filename}.")
            self.show_message()

        records_plugin_name = records_dict.get("summary", {}).get('plugin_name', None)
        logger.debug(f"Records being loaded are created by {records_plugin_name}")

        plugin_instance = self.select_plugin_instance(plugin_name)
        if records_plugin_name != plugin_instance.plugin_name:
            mbox = QMessageBox()
            mbox.setWindowTitle("Continue loading records?")
            mbox.setText(f"Records created by {records_plugin_name}, not by {plugin_instance.plugin_name}. Continue?")
            mbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            mbox.setDefaultButton(QMessageBox.No)
            result = mbox.exec()
            if result == QMessageBox.No:
                return
            else:
                self.switch_plugin(records_plugin_name)
                plugin_instance = self.select_plugin_instance(plugin_name)

        try:
            plugin_instance.load_records(records_filename)
        except Exception as exception:
            self.show_message(title = "Record loading error", message = str(exception))

        # labels not updated if the target plugin is not current
        self.update_labels()
        self.signal_restore_image_settings.emit()
        self.signal_update_image_view.emit()

    def save_records (self, records_filename, plugin_name = None, additional_settings = {}):
        plugin_instance = self.select_plugin_instance(plugin_name)

        try:
            plugin_instance.save_records(records_filename, settings = additional_settings)
        except Exception as exception:
            self.show_message(title = "Record saving error", message = str(exception))

        # labels not updated if the target plugin is not current
        self.update_labels()

    def clear_records (self, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        plugin_instance.clear_records()

        # labels not updated if the target plugin is not current
        self.update_labels()

    def is_records_modified (self, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        return plugin_instance.is_records_modified()

    def records_filename_filter_list (self, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        return [f"{key} ({" ".join(value)})" for key, value in plugin_instance.file_types.items()]

    def notify_plugins_stack_updated (self, stack):
        for instance in self.plugin_instance_dict.values():
            instance.update_stack_reference(stack)

    def notify_plugin_focus_recovery (self):
        self.current_instance.notice_focus_recovery()

    def plugin_records_dict (self, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        return plugin_instance.records_dict

    def suggest_records_filename (self, image_filename, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        return plugin_instance.suggest_filename(image_filename)

    def plugin_records_filename (self, plugin_name = None):
        plugin_instance = self.select_plugin_instance(plugin_name)
        return plugin_instance.records_filename

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def slot_switch_plugin (self, action):
        self.switch_plugin(action.text())

    def slot_plugin_help (self):
        self.show_message(title = "Quick help", message = self.current_instance.help_message())
        self.current_instance.notice_focus_recovery()

    def slot_update_image_view (self):
        self.signal_update_image_view.emit()

    def slot_update_mouse_cursor (self, cursor):
        self.signal_update_mouse_cursor.emit(cursor)

    def slot_select_image_by_tczindex (self, *tcz_index):
        self.signal_select_image_by_tczindex.emit(*tcz_index)

    def slot_focus_graphics_view (self):
        self.signal_focus_graphics_view.emit()

    def slot_records_updated (self):
        self.update_labels()
        self.signal_update_image_view.emit()



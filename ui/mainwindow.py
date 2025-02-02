#!/usr/bin/env python

import textwrap
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QProgressDialog, QApplication
from PySide6.QtCore import QFile, Qt, Signal
from PySide6.QtUiTools import QUiLoader
from ui import imagepanel, zoompanel, lutpanel, pluginpanel
from image import stack

class MainWindow (QMainWindow):
    signal_open_new_image = Signal(list)

    def __init__ (self, image_filename = None, records_filename = None, current_plugin_name = None):
        super().__init__()
        self.app_name = "MomoTrack"
        self.image_types = {"TIFF Image": ["*.tif", "*.tiff", "*.stk"]}

        self.setWindowTitle(self.app_name)

        self.image_filename = None
        self.records_filename = None

        self.load_ui()

        self.init_widgets()
        self.connect_menubar_to_slots()
        self.connect_signals_to_slots()

        try:
            if image_filename is not None and len(image_filename) > 0:
                self.load_image(image_filename)
            if records_filename is not None and len(records_filename) > 0:
                self.load_records(records_filename)
        except Exception:
            # throw exception to the main routine
            raise

    def load_ui (self):
        file = QFile(str(Path(__file__).parent.joinpath("mainwindow.ui")))
        file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui)
        self.setAcceptDrops(True)

        self.lut_panel = lutpanel.LutPanel(self.ui)
        self.zoom_panel = zoompanel.ZoomPanel(self.ui)
        self.image_panel = imagepanel.ImagePanel(self.ui)
        self.plugin_panel = pluginpanel.PluginPanel(self.ui)

    def resize_best (self):
        screen_size = self.screen().availableSize()
        width = int(screen_size.width() * 0.8)
        height = int(screen_size.height() * 0.8)
        self.resize(width, height)

    def init_widgets (self):
        self.image_panel.init_widgets()
        self.zoom_panel.init_widgets()
        self.lut_panel.init_widgets(self.image_panel.image_stack)
        self.update_image_view()
        self.update_window_title()

    def connect_menubar_to_slots (self):
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_records.triggered.connect(self.slot_load_records)
        self.ui.action_save_records.triggered.connect(self.slot_save_records)
        self.ui.action_save_records_as.triggered.connect(self.slot_save_records_as)
        self.ui.action_clear_records.triggered.connect(self.slot_clear_records)
        self.ui.action_zoom_in.triggered.connect(self.zoom_panel.slot_zoomed_in)
        self.ui.action_zoom_out.triggered.connect(self.zoom_panel.slot_zoomed_out)
        self.ui.action_zoom_reset.triggered.connect(self.zoom_panel.slot_zoom_reset)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_about_qt.triggered.connect(self.slot_about_qt)
        self.ui.action_plugin_help.triggered.connect(self.plugin_panel.slot_plugin_help)
        self.ui.action_viewer_help.triggered.connect(self.slot_viewer_help)

    def connect_signals_to_slots (self):
        # image panel
        self.image_panel.signal_image_index_changed.connect(self.slot_update_image_view)
        self.image_panel.signal_scene_mouse_pressed.connect(self.slot_scene_mouse_pressed)
        self.image_panel.signal_scene_mouse_moved.connect(self.slot_scene_mouse_moved)
        self.image_panel.signal_scene_mouse_released.connect(self.slot_scene_mouse_released)
        self.image_panel.signal_scene_key_pressed.connect(self.slot_scene_key_pressed)
        self.image_panel.signal_scene_key_released.connect(self.slot_scene_key_released)
        self.image_panel.signal_scene_wheel_moved.connect(self.slot_scene_wheel_moved)
        self.image_panel.connect_signals_to_slots()

        # zooming
        self.zoom_panel.connect_signals_to_slots()
        self.zoom_panel.signal_zoom_ratio_changed.connect(self.image_panel.slot_zoom_ratio_changed)

        # lut
        self.lut_panel.signal_current_lut_changed.connect(self.slot_update_image_view)
        self.lut_panel.signal_reset_current_lut_range.connect(self.slot_reset_current_lut_range)
        self.lut_panel.connect_signals_to_slots()

        # plugin
        self.plugin_panel.signal_plugin_changed.connect(self.slot_update_image_view)

    def open_multiple_images (self, image_filename_list):
        stack_exts = [item for values in self.image_types.values() for item in values]

        new_files = []
        for image_filename in image_filename_list:
            if any([Path(str(image_filename).lower()).match(ext) for ext in stack_exts]):
                if self.image_filename is None:
                    try:
                        self.load_image(image_filename)
                    except:
                        # does nothing because a message dialog is already shown
                        pass
                else:
                    new_files.append(image_filename)

        if len(new_files) > 0:
            self.signal_open_new_image.emit(new_files)

    def load_image (self, image_filename):
        # This function may throw an exception
        file = Path(image_filename)
        total_size = file.stat().st_size

        dialog = QProgressDialog("Loading: {0}".format(file.name), "Cancel", 0, 100)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.show()
        QApplication.processEvents()

        try:
            image_stack = stack.Stack()
            for read_size in image_stack.read_image_by_chunk(image_filename):
                dialog.setValue(int(read_size / total_size * 100))
                QApplication.processEvents()
                if dialog.wasCanceled():
                    return
        except:
            self.show_message(title = "Image opening error", message = f"Failed to open image: {image_filename}")
            raise

        self.image_panel.image_stack = image_stack
        self.image_filename = image_filename

        self.init_widgets()
        self.plugin_panel.update_plugin_stack_info(self.image_panel.image_stack)
        self.zoom_best()

    def load_records (self, records_filename):
        self.plugin_panel.load_records(records_filename)
        self.restore_settings(self.plugin_panel.current_records().get('viewer_settings', {}))

    def save_records (self, records_filename):
        settings = {'image_properties': self.archive_image_properties(), 
                    'viewer_settings': self.archive_viewer_settings()}
        self.plugin_panel.save_records(records_filename, settings = settings)

    def ask_records_filename (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a filename to save records.")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.plugin_class.file_types.items()])
        dialog.setViewMode(QFileDialog.List)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        if self.image_filename is not None:
            image_file = Path(self.image_filename)
            if image_file.exists():
                dialog.setDirectory(str(image_file.resolve().parent))
                dialog.selectFile(self.plugin_class.suggest_filename(self.image_filename))

        if dialog.exec() == False:
            return None
        
        return dialog.selectedFiles()[0]

    def clear_records (self):
        self.plugin_panel.clear_records()

    def clear_modified_flag (self, all_plugins = False):
        if all_plugins:
            plugin_module_list = self.plugin_panel.plugin_module_list
        else:
            plugin_module_list = [self.plugin_panel.current_module]

        for plugin_module in plugin_module_list:
            if plugin_module.is_records_modified():
                mbox = QMessageBox()
                mbox.setWindowTitle("Save Records?")
                mbox.setText(f"Record modified for {plugin_module.plugin_name}. Save?")
                mbox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                mbox.setDefaultButton(QMessageBox.Cancel)
                result = mbox.exec()
                if result == QMessageBox.Cancel:
                    return False
                elif result == QMessageBox.Discard:
                    plugin_module.clear_records()
                    return True
                else:
                    filename = self.ask_records_filename()
                    self.save_records(filename)
                    if plugin_module.is_records_modified():
                        return False

        self.plugin_panel.update_labels()
        return True

    def restore_settings(self, settings = None):
        if settings is None:
            settings = self.plugin_class.records_dict.get('viewer_settings', {})
        self.ui.slider_zstack.setValue(settings.get('z_index', 0))
        self.ui.slider_time.setValue(settings.get('t_index', 0))

        self.lut_panel.restore_lut_settings(settings.get('luts', []))
        self.lut_panel.set_current_channel(settings.get('channel', 0))
        self.ui.check_composite.setChecked(settings.get('composite', False))
        self.ui.check_lut_grayscale.setChecked(settings.get('lut_grayscale', False))

        self.zoom_panel.set_zoom(settings.get('zoom_ratio', 100))
        self.ui.gview_image.verticalScrollBar().setValue(settings.get('v_scroll', 0))
        self.ui.gview_image.horizontalScrollBar().setValue(settings.get('h_scroll', 0))

        self.update_image_view()

    def archive_viewer_settings (self):
        settings = {'z_index': self.ui.slider_zstack.value(),
                    't_index': self.ui.slider_time.value(),
                    'channel': self.ui.combo_channel.currentIndex(),
                    'composite': self.ui.check_composite.isChecked(),
                    'lut_grayscale': self.ui.check_lut_grayscale.isChecked(),
                    'luts': [lut.archive_settings() for lut in self.lut_panel.lut_list],
                    'zoom_ratio': self.zoom_panel.zoom_ratio,
                    'v_scroll': self.ui.gview_image.verticalScrollBar().value(),
                    'h_scroll': self.ui.gview_image.horizontalScrollBar().value(),
                    }
        return settings

    def archive_image_properties (self):
        settings = {'image_filename': self.image_filename}
        settings = settings | self.image_panel.image_stack.archive_properties()
        return settings

    def update_window_title (self):
        title = self.app_name
        if self.image_filename is not None:
            title = "{0} - {1}".format(title, Path(self.image_filename).name)
        self.setWindowTitle(title)

    def update_image_view (self):
        self.image_panel.channel = self.lut_panel.current_channel()
        self.image_panel.composite = self.lut_panel.is_composite()
        self.image_panel.lut_grayscale = self.lut_panel.is_lut_grayscale()

        self.lut_panel.update_lut_range_if_auto(self.image_panel.current_image())
        self.lut_panel.update_lut_view(self.image_panel.current_image())

        self.image_panel.update_image_scene(lut_list = self.lut_panel.lut_list, \
                                            item_list = self.plugin_class.list_scene_items(self.image_panel.image_stack,
                                                                                           self.image_panel.current_index()))


    def zoom_best (self):
        self.zoom_panel.zoom_best((self.image_panel.image_stack.width, self.image_panel.image_stack.height), \
                                  (self.ui.gview_image.size().width(), self.ui.gview_image.size().height()))

    def show_message (self, title = "No title", message = "Default message."):
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(message)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec()

    def slot_open_image (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select images to open.")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.image_types.items()])
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec():
            self.open_multiple_images(dialog.selectedFiles())

        self.plugin_panel.notice_focus_recovery()
        self.activateWindow()

    def slot_load_records (self):
        if self.image_filename is None:
            self.show_message(title = "Records loading error", message = "Open image before loading records.")
            return

        if self.clear_modified_flag() == False:
            return

        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a record to load.")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.plugin_class.file_types.items()])
        dialog.setViewMode(QFileDialog.List)

        image_file = Path(self.image_filename)
        if image_file.exists():
            dialog.setDirectory(str(image_file.resolve().parent))

        if dialog.exec():
            try:
                self.load_records(dialog.selectedFiles()[0])
            except:
                # does nothing because a message dialog is already shown
                pass
            self.update_image_view()

        self.plugin_panel.notice_focus_recovery()
        self.activateWindow()

    def slot_save_records (self):
        if self.plugin_class.records_filename is None:
            self.slot_save_records_as()
        else:
            try:
                self.save_records(self.plugin_class.records_filename)
            except:
                # does nothing because a message dialog is already shown
                pass

    def slot_save_records_as (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a filename to save records.")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.plugin_class.file_types.items()])
        dialog.setViewMode(QFileDialog.List)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        if self.image_filename is not None:
            image_file = Path(self.image_filename)
            if image_file.exists():
                dialog.setDirectory(str(image_file.resolve().parent))
                dialog.selectFile(self.plugin_class.suggest_filename(self.image_filename))

        if dialog.exec():
            try:
                self.save_records(dialog.selectedFiles()[0])
            except:
                # does nothing because a message dialog is already shown
                pass

        self.plugin_panel.notice_focus_recovery()
        self.activateWindow()

    def slot_clear_records (self):
        self.clear_records()

    def slot_focus_graphics_view (self):
        self.ui.gview_image.setFocus()
        self.activateWindow()

    def slot_viewer_help (self):
        message = textwrap.dedent('''\
        <b>Keys and mouse gestures:</b>
        <ul>
        <li> Left/Right keys to move the time forward or backward.</li>
        <li> Up/Down keys to increase or decrease the z-index.</li>
        <li> Shift + wheel to zoom in or zoom out.</li>
        </ul>
        <b>Note:</b> the settings of this viewer is saved in the record file
        created by the current plugin. See also the plugin help.
        ''')
        self.show_message(title = "Viewer help", message = message)
        self.plugin_class.focus_recovered()

    def slot_about_this (self):
        message = textwrap.dedent('''\
        <b>{0}</b><br><br>
        Object tracking system for time-lapse 2D/3D images.<br>
        Distributed under the MIT license.<br>
        Copyright 2021-2023 by Takushi Miyoshi (NIH/NIDCD).<br>
        Copyright 2024-2025 by Takushi Miyoshi (SIUSOM).
        '''.format(self.app_name))
        self.show_message(title = "About This", message = message)
        self.plugin_class.focus_recovered()

    def slot_about_qt (self):
        QApplication.aboutQt()
        self.plugin_class.focus_recovered()

    def slot_update_image_view (self):
        self.update_image_view()
        self.ui.gview_image.setFocus()

    def slot_reset_current_lut_range (self):
        self.lut_panel.reset_current_lut_range(self.image_panel.image_stack.image_array)
        self.update_image_view()

    def slot_scene_mouse_pressed (self, event):
        self.plugin_class.mouse_pressed(event, self.image_panel.image_stack, self.image_panel.current_index())
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_scene_mouse_moved (self, event):
        self.plugin_class.mouse_moved(event, self.image_panel.image_stack, self.image_panel.current_index())
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_scene_mouse_released (self, event):
        self.plugin_class.mouse_released(event, self.image_panel.image_stack, self.image_panel.current_index())
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_scene_wheel_moved (self, event):
        if event.modifiers() == Qt.ShiftModifier:
            if event.delta() > 0:
                self.zoom_panel.slot_zoomed_in()
            elif event.delta() < 0:
                self.zoom_panel.slot_zoomed_out()
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_scene_key_pressed (self, event):
        self.plugin_class.key_pressed(event, self.image_panel.image_stack, self.image_panel.current_index())
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_scene_key_released (self, event):
        self.plugin_class.key_released(event, self.image_panel.image_stack, self.image_panel.current_index())
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def slot_select_image_by_tczindex (self, time, channel, z_index):
        if channel != self.lut_panel.current_channel():
            self.ui.combo_channel.setCurrentIndex(channel)
        self.ui.slider_time.setValue(time)
        self.ui.slider_zstack.setValue(z_index)

    def slot_update_mouse_cursor (self, cursor):
        self.ui.setCursor(cursor)

    def slot_show_message (self, title, message):
        self.show_message(title, message)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            stack_exts = [item for values in self.image_types.values() for item in values]
            record_exts = [item for values in self.plugin_class.file_types.values() for item in values]

            files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
            stack_files = [file for file in files if any([Path(str(file).lower()).match(ext) for ext in stack_exts])]
            record_files = [file for file in files if any([Path(str(file).lower()).match(ext) for ext in record_exts])]
            error_files = [file for file in files if (file not in stack_files) and (file not in record_files)]

            if len(stack_files) > 0:
                self.open_multiple_images([str(file) for file in stack_files])
                error_files.extend(record_files)
            elif len(record_files) > 0:
                if self.image_filename is not None and len(record_files) == 1:
                    self.load_records(record_files[0])
                else:
                    error_files.extend(record_files)
            
            if len(error_files) > 0:
                self.show_message(title = "Drug and drop error", \
                                  message = "Unable to open: {0}".format(', '.join([str(file) for file in error_files])))

    def showEvent (self, event):
        self.update_image_view()
        self.plugin_panel.update_filename(self.plugin_class.records_filename, self.plugin_class.is_modified())

    def closeEvent (self, event):
        if self.clear_modified_flag():
            event.accept()
        else:
            event.ignore()


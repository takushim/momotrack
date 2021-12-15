#!/usr/bin/env python

from pathlib import Path
from importlib import import_module
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QProgressDialog, QApplication
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtCore import QFile, QTimer, Qt, Signal
from PySide6.QtUiTools import QUiLoader
from ui import imagepanel, zoompanel, lutpanel, pluginpanel
from image import stack

class MainWindow (QMainWindow):
    signal_open_new_image = Signal(list)

    def __init__ (self, image_filename = None, records_filename = None, plugin_name = None):
        super().__init__()
        self.app_name = "PyTrace"
        self.setWindowTitle(self.app_name)

        self.image_stack = stack.Stack()
        self.image_filename = image_filename
        self.records_filename = records_filename

        self.load_ui()

        self.plugin_package = 'plugin'
        self.default_plugin = 'base'
        self.load_plugins()

        self.init_widgets()
        if plugin_name is None:
            self.switch_plugin(self.plugin_list[0].plugin_name)
        elif plugin_name != self.plugin_module.plugin_name:
            self.switch_plugin(plugin_name)
        self.connect_menubar_to_slots()
        self.connect_signals_to_slots()

        if image_filename is not None and len(image_filename) > 0:
            self.load_image(image_filename)
        if records_filename is not None and len(records_filename) > 0:
            self.load_records(records_filename)

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
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(100)

    def init_widgets (self):
        self.image_panel.init_widgets(self.image_stack)
        self.zoom_panel.zoom_reset()
        self.lut_panel.init_widgets(self.image_stack)
        self.lut_panel.update_lut_view(self.image_panel.current_image(self.image_stack))
        self.image_panel.update_zoom(self.zoom_panel.zoom_ratio)
        self.update_image_view()
        self.update_window_title()

    def load_plugins (self):
        plugin_folder = str(Path(__file__).parent.parent.joinpath(self.plugin_package))
        self.plugin_list = []
        load_failed = []

        self.actgroup_plugin = QActionGroup(self.ui.menu_plugin)
        for module_file in Path(plugin_folder).iterdir():
            if module_file.name.startswith("_"):
                continue
            try:
                module = import_module(name = '{0}.{1}'.format(self.plugin_package, str(module_file.stem)))
                self.plugin_list.append(module)
            except ImportError:
                load_failed.append(str(module_file.stem))

        self.plugin_list = [plugin for plugin in self.plugin_list if plugin.priority >= 0]
        if len(self.plugin_list) == 0:
            self.plugin_list = [import_module(name = '{0}.{1}'.format(self.plugin_package, self.default_plugin))]

        self.plugin_list = sorted(self.plugin_list, key = lambda x: x.priority)
        for plugin in self.plugin_list:
            action = QAction(plugin.plugin_name, self.ui.menu_plugin, checkable = True, checked = (plugin is self.plugin_list[0]))
            self.ui.menu_plugin.addAction(action)
            self.actgroup_plugin.addAction(action)
        self.actgroup_plugin.setExclusive(True)

        self.init_plugin(self.plugin_list[0])    

        if len(load_failed) > 0:
            self.show_message("Plugin error", "Failed to load: {0}".format(', '.join(load_failed)))

    def connect_menubar_to_slots (self):
        self.ui.action_quit.triggered.connect(self.close)
        self.ui.action_open_image.triggered.connect(self.slot_open_image)
        self.ui.action_load_records.triggered.connect(self.slot_load_records)
        self.ui.action_save_records.triggered.connect(self.slot_save_records)
        self.ui.action_save_records_as.triggered.connect(self.slot_save_records_as)
        self.ui.action_clear_records.triggered.connect(self.slot_clear_records)
        self.ui.action_zoom_in.triggered.connect(self.slot_zoomed_in)
        self.ui.action_zoom_out.triggered.connect(self.slot_zoomed_out)
        self.ui.action_zoom_reset.triggered.connect(self.slot_zoom_reset)
        self.ui.action_about_this.triggered.connect(self.slot_about_this)
        self.ui.action_quick_help.triggered.connect(self.slot_quick_help)

    def connect_signals_to_slots (self):
        # scene
        self.image_panel.scene.mousePressEvent = self.slot_scene_mouse_clicked
        self.image_panel.scene.mouseMoveEvent = self.slot_scene_mouse_moved
        self.image_panel.scene.mouseReleaseEvent = self.slot_scene_mouse_released
        self.image_panel.scene.keyPressEvent = self.slot_scene_key_pressed
        self.image_panel.scene.keyReleaseEvent = self.slot_scene_key_released
        self.image_panel.scene.wheelEvent = self.slot_scene_wheel_moved

        # time and zstack
        self.ui.slider_time.valueChanged.connect(self.slot_image_index_changed)
        self.ui.slider_zstack.valueChanged.connect(self.slot_image_index_changed)
        self.ui.button_play.clicked.connect(self.slot_slideshow_switched)
        self.ui.spin_fps.valueChanged.connect(self.slot_slideshow_changed)
        self.play_timer.timeout.connect(self.slot_slideshow_timeout)

        # zooming
        self.ui.button_zoom_in.clicked.connect(self.slot_zoomed_in)
        self.ui.button_zoom_out.clicked.connect(self.slot_zoomed_out)
        self.ui.button_zoom_reset.clicked.connect(self.slot_zoom_reset)

        # lut
        self.ui.combo_channel.currentIndexChanged.connect(self.slot_channel_changed)
        self.ui.check_composite.stateChanged.connect(self.slot_channel_changed)
        self.ui.check_color_always.stateChanged.connect(self.slot_channel_changed)
        self.ui.check_invert_lut.stateChanged.connect(self.slot_lut_changed)
        self.ui.combo_lut.currentIndexChanged.connect(self.slot_lut_changed)
        self.ui.combo_bits.currentIndexChanged.connect(self.slot_bits_changed)
        self.ui.check_auto_lut.stateChanged.connect(self.slot_auto_lut_changed)
        self.ui.dspin_auto_cutoff.valueChanged.connect(self.slot_auto_lut_changed)
        self.ui.slider_cutoff_lower.valueChanged.connect(self.slot_lut_lower_changed)
        self.ui.slider_cutoff_upper.valueChanged.connect(self.slot_lut_upper_changed)
        self.ui.button_reset_lut.clicked.connect(self.slot_reset_lut)

        # plugin
        self.actgroup_plugin.triggered.connect(self.slot_switch_plugin)

    def open_images (self, image_filename_list):
        stack_exts = [item for values in stack.file_types.values() for item in values]

        new_files = []
        for image_filename in image_filename_list:
            if any([Path(str(image_filename).lower()).match(ext) for ext in stack_exts]):
                if self.image_filename is None:
                    self.load_image(image_filename)
                else:
                    new_files.append(image_filename)

        if len(new_files) > 0:
            self.signal_open_new_image.emit(new_files)

    def resize_best (self):
        screen_size = self.screen().availableSize()
        width = int(screen_size.width() * 0.8)
        height = int(screen_size.height() * 0.8)
        self.resize(width, height)

    def zoom_best (self):
        self.zoom_panel.zoom_best((self.image_stack.width, self.image_stack.height), \
                                  (self.ui.gview_image.size().width(), self.ui.gview_image.size().height()))
        self.image_panel.update_zoom(self.zoom_panel.zoom_ratio)

    def load_image (self, image_filename):
        try:
            file = Path(image_filename)
            total_size = file.stat().st_size

            dialog = QProgressDialog("Loading: {0}".format(file.name), "Cancel", 0, 100)
            dialog.setWindowModality(Qt.WindowModal)
            dialog.show()
            QApplication.processEvents()

            image_stack = stack.Stack()
            for read_size in image_stack.read_image_by_chunk(image_filename):
                dialog.setValue(int(read_size / total_size * 100))
                if dialog.wasCanceled():
                    raise OSError()

            self.image_stack = image_stack
            self.image_filename = image_filename

        except OSError:
            self.image_filename = None
            self.image_stack = stack.Stack()
            self.show_message(title = "Image opening error", message = "Failed to open image: {0}".format(image_filename))

        finally:
            self.init_widgets()
            self.plugin_class.update_stack_info(self.image_stack)
            self.zoom_best()

    def load_records (self, records_filename):
        try:
            self.plugin_class.load_records(records_filename)
            self.records_filename = records_filename
            self.plugin_panel.update_filename(records_filename)
        except OSError:
            print(records_filename)
            self.show_message(title = "Records loading error", message = "Failed to load records: {0}".format(records_filename))

    def save_records (self, records_filename):
        try:
            self.plugin_class.save_records(records_filename, settings = self.archive_settings())
            self.records_filename = records_filename
            self.plugin_panel.update_filename(records_filename)
        except OSError:
            self.show_message(title = "Records saving error", message = "Failed to save records: {0}".format(records_filename))

    def clear_records (self):
        self.plugin_class.clear_records()
        self.records_filename = None

    def archive_settings (self):
        return {'image_filename': self.image_filename}

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
                self.save_records(self.records_filename, self.image_filename)
                if self.plugin_class.is_modified():
                    return False
        return True

    def switch_plugin (self, name):
        module = next((x for x in self.plugin_list if x.plugin_name == name), None)

        if module is None or self.clear_modified_flag() == False:
            return

        self.init_plugin(module)
        self.update_image_view()
        self.plugin_class.update_stack_info(self.image_stack)

    def init_plugin (self, module):
        self.plugin_module = module
        self.plugin_class = getattr(module, module.class_name)()
        self.plugin_panel.update_title(module.plugin_name)
        self.plugin_panel.update_widgets(self.plugin_class)
        self.plugin_class.signal_update_scene.connect(self.slot_update_scene)
        self.plugin_class.signal_update_lut.connect(self.slot_update_lut)
        self.plugin_class.signal_reset_panels.connect(self.slot_reset_panels)
        self.plugin_class.signal_update_mouse_cursor.connect(self.slot_update_mouse_cursor)
        self.plugin_class.signal_move_by_tczindex.connect(self.slot_move_by_tczindex)

    def update_window_title (self):
        title = self.app_name
        if self.image_filename is not None:
            title = "{0} - {1}".format(title, Path(self.image_filename).name)
        self.setWindowTitle(title)

    def update_image_view (self):
        self.image_panel.channel = self.lut_panel.current_channel()
        self.image_panel.composite = self.lut_panel.is_composite()
        self.image_panel.color_always = self.lut_panel.color_always()
        self.image_panel.update_image_scene(self.image_stack, lut_list = self.lut_panel.lut_list, \
                                            item_list = self.plugin_class.list_scene_items(self.image_stack, self.image_panel.current_index()))

        self.lut_panel.update_lut_view(self.image_panel.current_image(self.image_stack))

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
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in stack.file_types.items()])
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec():
            self.open_images(dialog.selectedFiles())

    def slot_load_records (self):
        if self.clear_modified_flag() == False:
            return

        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a record to load.")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.plugin_class.file_types.items()])
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec():
            self.load_records(dialog.selectedFiles()[0])
            self.update_image_view()

    def slot_save_records (self):
        if self.records_filename is None:
            self.slot_save_records_as()
        else:
            self.save_records(self.records_filename, self.image_filename)

    def slot_save_records_as (self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select a filename to save records.")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(["{0} ({1})".format(key, " ".join(value)) for key, value in self.plugin_class.file_types.items()])
        dialog.setViewMode(QFileDialog.List)
        dialog.selectFile(self.plugin_class.suggest_filename(self.image_filename))

        if dialog.exec():
            self.save_records(dialog.selectedFiles()[0], self.image_filename)

    def slot_clear_records (self):
        self.clear_records()
        self.update_image_view()

    def slot_quick_help (self):
        self.show_message(title = "Quick help", message = self.plugin_class.help_message())

    def slot_about_this (self):
        self.show_message(title = "About This",
                          message = "Object tracking system for time-lapse 2D/3D images.\n" +
                                    "Copyright 2021 by Takushi Miyoshi (NIH/NIDCD).")

    def slot_scene_mouse_clicked (self, event):
        self.plugin_class.mouse_clicked(event, self.image_stack, self.image_panel.current_index())

    def slot_scene_mouse_moved (self, event):
        self.plugin_class.mouse_moved(event, self.image_stack, self.image_panel.current_index())

    def slot_scene_mouse_released (self, event):
        self.plugin_class.mouse_released(event, self.image_stack, self.image_panel.current_index())

    def slot_scene_wheel_moved (self, event):
        if event.modifiers() == Qt.SHIFT:
            if event.delta() > 0:
                self.slot_zoomed_in()
            elif event.delta() < 0:
                self.slot_zoomed_out()

    def slot_scene_key_pressed (self, event):
        if event.key() == Qt.Key_Right:
            self.ui.slider_time.setValue(min(self.ui.slider_time.value() + 1,  self.image_stack.t_count - 1))
        elif event.key() == Qt.Key_Left:
            self.ui.slider_time.setValue(max(self.ui.slider_time.value() - 1, 0))
        elif event.key() == Qt.Key_Up:
            self.ui.slider_zstack.setValue(min(self.ui.slider_zstack.value() + 1,  self.image_stack.z_count - 1))
        elif event.key() == Qt.Key_Down:
            self.ui.slider_zstack.setValue(max(self.ui.slider_zstack.value() - 1, 0))
        else:
            self.plugin_class.key_pressed(event, self.image_stack, self.image_panel.current_index())

    def slot_scene_key_released (self, event):
        self.plugin_class.key_released(event, self.image_stack, self.image_panel.current_index())

    def slot_image_index_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack))
        self.update_image_view()

    def slot_channel_changed (self):
        self.lut_panel.update_channel_widgets()
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack))
        self.update_image_view()

    def slot_lut_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack))
        else:
            self.lut_panel.update_current_lut()
        self.update_image_view()

    def slot_bits_changed (self):
        self.lut_panel.update_current_bits()
        self.update_image_view()

    def slot_lut_lower_changed (self):
        self.lut_panel.adjust_slider_upper()
        self.lut_panel.update_current_lut()
        self.update_image_view()

    def slot_lut_upper_changed (self):
        self.lut_panel.adjust_slider_lower()
        self.lut_panel.update_current_lut()
        self.update_image_view()
    
    def slot_auto_lut_changed (self):
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack))
            self.update_image_view()

    def slot_reset_lut (self):
        self.lut_panel.reset_current_lut()
        self.update_image_view()

    def slot_zoomed_in (self):
        self.zoom_panel.zoom_in()
        self.image_panel.update_zoom(self.zoom_panel.zoom_ratio)

    def slot_zoomed_out (self):
        self.zoom_panel.zoom_out()
        self.image_panel.update_zoom(self.zoom_panel.zoom_ratio)

    def slot_zoom_reset (self):
        self.zoom_panel.zoom_reset()
        self.image_panel.update_zoom(self.zoom_panel.zoom_ratio)

    def slot_slideshow_switched (self):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.ui.button_play.setText("Play")
        else:
            self.play_timer.start()
            self.ui.button_play.setText("Stop")

    def slot_slideshow_changed (self):
        self.play_timer.setInterval(1000 / self.ui.spin_fps.value())

    def slot_slideshow_timeout (self):
        self.ui.slider_time.setValue((self.ui.slider_time.value() + 1) % self.image_stack.t_count)

    def slot_switch_plugin (self, action):
        self.switch_plugin(action.text())

    def slot_update_scene (self):
        self.update_image_view()

    def slot_update_lut (self):
        self.lut_panel.init_luts(self.image_stack)
        if self.lut_panel.is_auto_lut():
            self.lut_panel.set_auto_cutoff(self.image_panel.current_image(self.image_stack))
        else:
            self.lut_panel.update_current_lut()
        self.update_image_view()

    def slot_move_by_tczindex (self, time, channel, z_index):
        if channel != self.lut_panel.current_channel():
            self.ui.combo_channel.setCurrentIndex(channel)
        self.ui.slider_time.setValue(time)
        self.ui.slider_zstack.setValue(z_index)

    def slot_reset_panels (self):
        self.init_widgets()

    def slot_update_mouse_cursor (self, cursor):
        self.ui.setCursor(cursor)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            stack_exts = [item for values in stack.file_types.values() for item in values]
            record_exts = [item for values in self.plugin_class.file_types.values() for item in values]

            files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
            stack_files = [file for file in files if any([Path(str(file).lower()).match(ext) for ext in stack_exts])]
            record_files = [file for file in files if any([Path(str(file).lower()).match(ext) for ext in record_exts])]
            error_files = [file for file in files if (file not in stack_files) and (file not in record_files)]

            if len(stack_files) > 0:
                self.open_images([str(file) for file in stack_files])
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

    def closeEvent (self, event):
        if self.clear_modified_flag():
            event.accept()
        else:
            event.ignore()


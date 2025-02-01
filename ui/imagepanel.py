#!/usr/bin/env python

import numpy as np
from PySide6.QtCore import Qt, QObject, Signal, QTimer, QEvent
from PySide6.QtWidgets import QGraphicsScene, QSlider, QGraphicsPixmapItem, QLineEdit
from PySide6.QtGui import QImage, QPixmap
from image import stack

class ImagePanel (QObject):
    signal_image_index_changed = Signal()
    signal_scene_mouse_pressed = Signal(QEvent)
    signal_scene_mouse_moved = Signal(QEvent)
    signal_scene_mouse_released = Signal(QEvent)
    signal_scene_wheel_moved = Signal(QEvent)
    signal_scene_key_pressed = Signal(QEvent)
    signal_scene_key_released = Signal(QEvent)

    def __init__ (self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(self.ui.palette().window())
        self.ui.gview_image.setScene(self.scene)
        self.channel = 0
        self.composite = False
        self.color_always = False
        self.image_stack = stack.Stack()
        self.image_stack.alloc_zero_image()

    def init_widgets (self):
        # Time slider
        self.ui.slider_time.setMinimum(0)
        self.ui.slider_time.setMaximum(self.image_stack.t_count - 1)
        self.ui.slider_time.setValue(0)
        self.ui.slider_time.setTickInterval(10)
        self.ui.slider_time.setTickPosition(QSlider.TicksBelow)

        # Z slider
        self.ui.slider_zstack.setMinimum(0)
        self.ui.slider_zstack.setMaximum(self.image_stack.z_count - 1)
        self.ui.slider_zstack.setValue(0)
        self.ui.slider_zstack.setTickInterval(1)
        self.ui.slider_zstack.setTickPosition(QSlider.TicksBelow)

        # timer (cannot start a timer in the event loop. bug?)
        self.ui.spin_fps.setValue(10)
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(1000 / self.ui.spin_fps.value())
        self.play_timer.start()

    def connect_signals_to_slots (self):
        self.ui.slider_time.valueChanged.connect(self.slot_image_index_changed)
        self.ui.slider_zstack.valueChanged.connect(self.slot_image_index_changed)
        self.ui.button_play.clicked.connect(self.slot_slideshow_play_toggled)
        self.ui.spin_fps.valueChanged.connect(self.slot_slideshow_fps_changed)
        self.ui.spin_fps.editingFinished.connect(self.slot_slideshow_fps_changed)

        self.scene.mousePressEvent = self.slot_scene_mouse_pressed
        self.scene.mouseMoveEvent = self.slot_scene_mouse_moved
        self.scene.mouseReleaseEvent = self.slot_scene_mouse_released
        self.scene.keyPressEvent = self.slot_scene_key_pressed
        self.scene.keyReleaseEvent = self.slot_scene_key_released
        self.scene.wheelEvent = self.slot_scene_wheel_moved

    def update_status (self):
        status = "T: {0}/{1}, Z: {2}/{3}".format(self.ui.slider_time.value(), self.ui.slider_time.maximum(),
                                                 self.ui.slider_zstack.value(), self.ui.slider_zstack.maximum())
        self.ui.label_status.setText(status)

    def update_image_scene (self, lut_list, item_list = []):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()

        if self.composite:
            final_image = np.zeros((self.image_stack.height, self.image_stack.width, 3), dtype = np.uint8)
            for channel in range(self.image_stack.c_count):
                image = self.image_stack.image_array[t_index, channel, z_index]
                image = np.stack(lut_list[channel].apply_lut_rgb(image), axis = -1)
                final_image = np.maximum(final_image, image)
            qimage = QImage(final_image.data, self.image_stack.width, self.image_stack.height, QImage.Format_RGB888)
        else:
            if self.color_always:
                image = self.image_stack.image_array[t_index, self.channel, z_index]
                image = np.stack(lut_list[self.channel].apply_lut_rgb(image), axis = -1)
                qimage = QImage(image.data, self.image_stack.width, self.image_stack.height, QImage.Format_RGB888)
            else:
                image = self.image_stack.image_array[t_index, self.channel, z_index]
                image = lut_list[self.channel].apply_lut_gray(image)
                qimage = QImage(image.data, self.image_stack.width, self.image_stack.height, QImage.Format_Grayscale8)

        self.scene.clear()
        pixmap_item = QGraphicsPixmapItem()
        pixmap_item.setPixmap(QPixmap(qimage))
        self.scene.addItem(pixmap_item)

        for item in item_list:
            self.scene.addItem(item)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.update_status()

    def current_image (self):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()
        return self.image_stack.image_array[t_index, self.channel, z_index]

    def current_index (self):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()
        return [t_index, self.channel, z_index]
    
    def slot_scene_mouse_pressed (self, event):
        self.signal_scene_mouse_pressed.emit(event)

    def slot_scene_mouse_moved (self, event):
        self.signal_scene_mouse_moved.emit(event)

    def slot_scene_mouse_released (self, event):
        self.signal_scene_mouse_released.emit(event)

    def slot_scene_wheel_moved (self, event):
        self.signal_scene_wheel_moved.emit(event)

    def slot_scene_key_pressed (self, event):
        if event.modifiers() == Qt.NoModifier:
            if event.key() == Qt.Key_Right:
                self.ui.slider_time.setValue(min(self.ui.slider_time.value() + 1,  self.ui.slider_time.maximum() - 1))
            elif event.key() == Qt.Key_Left:
                self.ui.slider_time.setValue(max(self.ui.slider_time.value() - 1, 0))
            elif event.key() == Qt.Key_Home:
                self.ui.slider_time.setValue(0)
            elif event.key() == Qt.Key_End:
                self.ui.slider_time.setValue(self.ui.slider_time.value())
            elif event.key() == Qt.Key_Up:
                self.ui.slider_zstack.setValue(min(self.ui.slider_zstack.value() + 1,  self.ui.slider_zstack.maximum() - 1))
            elif event.key() == Qt.Key_Down:
                self.ui.slider_zstack.setValue(max(self.ui.slider_zstack.value() - 1, 0))
        self.signal_scene_key_pressed.emit(event)

    def slot_scene_key_released (self, event):
        self.signal_scene_key_released.emit(event)

    def slot_image_index_changed (self):
        self.signal_image_index_changed.emit()

    def slot_zoom_ratio_changed (self, zoom_ratio):
        self.ui.gview_image.resetTransform()
        self.ui.gview_image.scale(zoom_ratio / 100, zoom_ratio / 100)

    def slot_slideshow_play_toggled (self):
        if self.ui.button_play.text() == "Stop":
            self.ui.button_play.setText("Play")
            self.play_timer.timeout.disconnect()
        else:
            self.ui.button_play.setText("Stop")
            self.play_timer.timeout.connect(self.slot_slideshow_timer_timeout)

    def slot_slideshow_timer_timeout (self):
        self.ui.slider_time.setValue((self.ui.slider_time.value() + 1) % (self.ui.slider_time.maximum() + 1))

    def slot_slideshow_fps_changed (self):
        self.play_timer.setInterval(1000 / self.ui.spin_fps.value())
        self.ui.spin_fps.findChild(QLineEdit).deselect()



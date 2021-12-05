#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtWidgets import QGraphicsScene, QSlider
from PySide6.QtGui import QImage, QPixmap

class ImagePanel:
    def __init__ (self, ui):
        self.ui = ui
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(self.ui.palette().window())
        self.ui.gview_image.setScene(self.scene)
        self.channel = 0
        self.composite = False
        self.color_always = False

    def init_widgets (self, stack):
        self.ui.slider_time.setMaximum(0)
        self.ui.slider_time.setValue(0)
        self.ui.slider_zstack.setMaximum(0)
        self.ui.slider_zstack.setValue(0)

        # Time slider
        self.ui.slider_time.setMinimum(0)
        self.ui.slider_time.setMaximum(stack.t_count - 1)
        self.ui.slider_time.setValue(0)
        self.ui.slider_time.setTickInterval(10)
        self.ui.slider_time.setTickPosition(QSlider.TicksBelow)
        # Z slider
        self.ui.slider_zstack.setMinimum(0)
        self.ui.slider_zstack.setMaximum(stack.z_count - 1)
        self.ui.slider_zstack.setValue(0)
        self.ui.slider_zstack.setTickInterval(1)
        self.ui.slider_zstack.setTickPosition(QSlider.TicksBelow)

    def update_status (self, stack):
        status = "T: {0}/{1}, Z: {2}/{3}".format(self.ui.slider_time.value(), stack.t_count - 1,
                                                 self.ui.slider_zstack.value(), stack.z_count - 1,)
        self.ui.label_status.setText(status)

    def update_zoom (self, zoom_ratio):
        self.ui.gview_image.resetTransform()
        self.ui.gview_image.scale(zoom_ratio / 100, zoom_ratio / 100)

    def update_image_scene (self, stack, lut_list, item_list = []):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()

        if self.composite:
            final_image = np.zeros((stack.height, stack.width, 3), dtype = np.uint8)
            for channel in range(stack.c_count):
                image = stack.image_array[t_index, channel, z_index]
                image = np.stack(lut_list[channel].apply_lut_rgb(image), axis = -1)
                final_image = np.maximum(final_image, image)
            qimage = QImage(final_image.data, stack.width, stack.height, QImage.Format_RGB888)
        else:
            if self.color_always:
                image = stack.image_array[t_index, self.channel, z_index]
                image = np.stack(lut_list[self.channel].apply_lut_rgb(image), axis = -1)
                qimage = QImage(image.data, stack.width, stack.height, QImage.Format_RGB888)
            else:
                image = stack.image_array[t_index, self.channel, z_index]
                image = lut_list[self.channel].apply_lut_gray(image)
                qimage = QImage(image.data, stack.width, stack.height, QImage.Format_Grayscale8)

        self.scene.clear()
        self.scene.addPixmap(QPixmap(qimage))

        for item in item_list:
            self.scene.addItem(item)

        self.update_status(stack)

    def current_image (self, stack):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()
        return stack.image_array[t_index, self.channel, z_index]

    def current_index (self):
        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()
        return [t_index, self.channel, z_index]

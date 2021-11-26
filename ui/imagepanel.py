#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtWidgets import QGraphicsScene, QSlider
from PySide6.QtGui import QImage, QPixmap

class ImagePanel:
    def __init__ (self, ui):
        self.ui = ui
        self.scene = QGraphicsScene()
        self.ui.gview_image.setScene(self.scene)

    def init_sliders (self, stack):
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

    def update_image_scene (self, stack, zoom_ratio = 100):
        self.ui.gview_image.resetTransform()
        self.ui.gview_image.scale(zoom_ratio / 100, zoom_ratio / 100)

        t_index = self.ui.slider_time.value()
        z_index = self.ui.slider_zstack.value()

        image = stack.image_array[t_index, 0, z_index].astype(float)
        image = ((image - np.min(image)) / np.ptp(image) * 255).astype(np.uint8)

        qimage = QImage(image.data, stack.width, stack.height, QImage.Format_Grayscale8)
        pixmap = QPixmap(qimage)

        self.scene.clear()
        self.scene.addPixmap(pixmap)

        self.update_status(stack)


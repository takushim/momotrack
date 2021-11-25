#!/usr/bin/env python

import sys
import numpy as np
from PySide6.QtWidgets import QSlider
from PySide6.QtGui import QPixmap, QImage

def set_sliders (ui, stack):
    # Time slider
    ui.slider_time.setMinimum(0)
    ui.slider_time.setMaximum(stack.t_count - 1)
    ui.slider_time.setValue(0)
    ui.slider_time.setTickInterval(10)
    ui.slider_time.setTickPosition(QSlider.TicksBelow)
    # Z slider
    ui.slider_zstack.setMinimum(0)
    ui.slider_zstack.setMaximum(stack.t_count - 1)
    ui.slider_zstack.setValue(0)
    ui.slider_zstack.setTickInterval(10)
    ui.slider_zstack.setTickPosition(QSlider.TicksBelow)

def update_status (ui, stack):
    status = "T: {0}/{1}, Z: {2}/{3}".format(ui.slider_time.value(), stack.t_count - 1,
                                             ui.slider_zstack.value(), stack.z_count - 1,)
    ui.label_status.setText(status)

def update_image_view (ui, scene, stack):
    #image = stack.image_array[0, 0, 10].astype(float)
    #image = ((image - np.min(image)) / np.ptp(image) * 255).astype(np.uint8)
    #print(image.data)

    #qimage = QImage(image.data, stack.width, stack.height, format = QImage.Format_Grayscale8)
    qimage = QImage("test/lena_std.tif")
    pixmap = QPixmap(qimage)
    scene.addPixmap(pixmap)
    ui.gview_image.setScene(scene)



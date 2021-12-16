#!/usr/bin/env python

import numpy as np
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QColor
from image import lut

class LutPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.ui.combo_lut.addItems([item for item in lut.lut_dict])
        self.ui.combo_bits.addItems(["Auto"] + [item for item in lut.bit_dict])

    def init_widgets (self, stack):
        self.init_luts(stack)
        self.update_boxes()
        self.update_sliders()
        self.update_labels()

        self.scene_lut = QGraphicsScene()
        self.scene_lut.setBackgroundBrush(QColor('white'))
        self.ui.gview_lut.setScene(self.scene_lut)

    def init_luts (self, stack):
        self.lut_list = []

        if stack is None:
            self.lut_list.append(lut.LUT())
        else:
            for channel in range(stack.c_count):
                lut_name = lut.lut_names[channel % len(lut.lut_names)]
                image_lut = lut.LUT(lut_name = lut_name, pixel_values = stack.image_array[:, channel])
                self.lut_list.append(image_lut)

    def update_boxes (self):
        self.ui.combo_channel.blockSignals(True)
        self.ui.combo_channel.clear()
        self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(len(self.lut_list))])
        self.ui.combo_channel.blockSignals(False)

        self.ui.combo_lut.setCurrentIndex(0)
        self.ui.combo_lut.setEnabled(self.ui.check_color_always.isChecked())

        lut = self.lut_list[0]
        self.ui.combo_bits.setCurrentText("Auto" if lut.bit_auto else lut.bit_mode)
        self.ui.check_auto_lut.setChecked(lut.auto_lut)
        self.ui.dspin_auto_cutoff.setValue(lut.auto_cutoff)

    def update_sliders (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        bit_range = current_lut.bit_range()

        self.ui.slider_lut_upper.blockSignals(True)
        self.ui.slider_lut_lower.blockSignals(True)

        self.ui.slider_lut_upper.setMinimum(bit_range[0])
        self.ui.slider_lut_upper.setMaximum(bit_range[1])
        self.ui.slider_lut_lower.setMinimum(bit_range[0])
        self.ui.slider_lut_lower.setMaximum(bit_range[1])

        self.ui.slider_lut_upper.setValue(current_lut.lut_upper)
        self.ui.slider_lut_lower.setValue(current_lut.lut_lower)

        self.ui.slider_lut_upper.blockSignals(False)
        self.ui.slider_lut_lower.blockSignals(False)

    def update_labels (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        bit_range = current_lut.bit_range()

        if current_lut.bit_mode == "Float":
            self.ui.label_bitrange_lower.setText("{0:.2e}".format(bit_range[0]))
            self.ui.label_bitrange_upper.setText("{0:.2e}".format(bit_range[1]))
            self.ui.label_lut_lower.setText("Lower limit: {0:.2e}".format(current_lut.lut_lower))
            self.ui.label_lut_upper.setText("Upper limit: {0:.2e}".format(current_lut.lut_upper))
        else:
            self.ui.label_bitrange_lower.setText("{0:d}".format(bit_range[0]))
            self.ui.label_bitrange_upper.setText("{0:d}".format(bit_range[1]))
            self.ui.label_lut_lower.setText("Lower limit: {0:d}".format(current_lut.lut_lower))
            self.ui.label_lut_upper.setText("Upper limit: {0:d}".format(current_lut.lut_upper))

    def adjust_slider_lower (self):
        self.ui.slider_lut_lower.setValue(min(self.ui.slider_lut_upper.value(), self.ui.slider_lut_lower.value()))
        self.update_current_lut()

    def adjust_slider_upper (self):
        self.ui.slider_lut_upper.setValue(max(self.ui.slider_lut_upper.value(), self.ui.slider_lut_lower.value()))
        self.update_current_lut()

    def update_current_lut (self):
        self.ui.check_auto_lut.setChecked(False)
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.lut_lower = self.ui.slider_lut_lower.value()
        current_lut.lut_upper = self.ui.slider_lut_upper.value()
        current_lut.lut_invert = self.ui.check_invert_lut.isChecked()
        current_lut.lut_name = self.ui.combo_lut.currentText()
        current_lut.bit_auto = (self.ui.combo_bits.currentText() == "Auto")
        self.update_labels()

    def reset_current_lut (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.bit_auto = True
        current_lut.reset_bit_mode()
        current_lut.reset_cutoff()
        self.ui.check_auto_lut.setChecked(False)
        self.update_channel_widgets()
        self.update_sliders()
        self.update_labels()

    def set_auto_cutoff (self, image):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.set_auto_cutoff(image, self.ui.dspin_auto_cutoff.value())
        current_lut.lut_invert = self.ui.check_invert_lut.isChecked()
        current_lut.lut_name = self.ui.combo_lut.currentText()

        self.ui.slider_lut_upper.blockSignals(True)
        self.ui.slider_lut_lower.blockSignals(True)
        self.ui.slider_lut_upper.setValue(current_lut.lut_upper)
        self.ui.slider_lut_lower.setValue(current_lut.lut_lower)
        self.ui.slider_lut_upper.blockSignals(False)
        self.ui.slider_lut_lower.blockSignals(False)

        self.ui.check_auto_lut.setChecked(True)
        self.update_labels()

    def update_current_bits (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]

        bit_mode = self.ui.combo_bits.currentText()
        if bit_mode == "Auto":
            current_lut.reset_bit_mode()
            current_lut.bit_auto = True
        else:
            current_lut.bit_mode = self.ui.combo_bits.currentText()
            current_lut.bit_auto = False
        
        self.update_sliders()
        self.update_labels()

    def update_channel_widgets (self):
        if self.ui.check_composite.isChecked() or self.ui.check_color_always.isChecked():
            self.ui.combo_lut.setEnabled(True)
        else:
            self.ui.combo_lut.setEnabled(False)

        if self.ui.check_composite.isChecked():
            self.ui.check_color_always.setEnabled(False)
        else:
            self.ui.check_color_always.setEnabled(True)

        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        self.ui.combo_lut.setCurrentText(current_lut.lut_name)
        if current_lut.bit_auto:
            self.ui.combo_bits.setCurrentText("Auto")
        else:
            self.ui.combo_bits.setCurrentText(current_lut.bit_mode)

        self.update_sliders()
        self.update_labels()

    def update_lut_view (self, image):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        bit_range = current_lut.bit_range()

        width = self.ui.gview_lut.width()
        height = self.ui.gview_lut.height()
        self.scene_lut.clear()
        self.scene_lut.setSceneRect(0, 0, width, height)

        hists, bins = np.histogram(image, bins = int(width), range = current_lut.bit_range())
        max_hist = np.max(hists)
        for index, hist in enumerate(hists):
            x = width * (bins[index] - np.min(bins)) / np.ptp(bins)
            y_bottom = height
            y_top = height * (1 - float(hist) / max_hist)
            self.scene_lut.addLine(x, y_bottom, x, y_top, QColor('gray'))

        if np.isclose(bit_range[0], bit_range[1]) == False:
            x_lower = width * (current_lut.lut_lower - bit_range[0]) / (bit_range[1] - bit_range[0])
            x_upper = width * (current_lut.lut_upper - bit_range[0]) / (bit_range[1] - bit_range[0])
            self.scene_lut.addLine(x_upper, 0, x_upper, height, QColor('black'))
            self.scene_lut.addLine(x_lower, height, x_upper, 0)

    def current_channel (self):
        return self.ui.combo_channel.currentIndex()

    def color_always (self):
        return self.ui.check_color_always.isChecked()

    def is_composite (self):
        return self.ui.check_composite.isChecked()
    
    def is_auto_lut (self):
        return self.ui.check_auto_lut.isChecked()

#!/usr/bin/env python

import sys
import numpy as np
from numpy.lib.function_base import percentile
from image import lut

class LutPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.ui.combo_lut.addItems([item for item in lut.lut_dict])
        self.ui.combo_bits.addItems(["Auto"] + [item for item in lut.bit_dict])
        self.init_widgets()

    def init_widgets (self, stack = None):
        self.lut_list = []
        self.ui.combo_lut.setEnabled(True)
        self.ui.combo_channel.clear()

        if stack is not None:
            for channel in range(stack.c_count):
                lut_name = lut.lut_names[channel % len(lut.lut_names)]
                image_lut = lut.LUT(lut_name = lut_name, pixel_values = stack.image_array[:, channel], lut_invert = False, bit_auto = True)
                self.lut_list.append(image_lut)
            self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(stack.c_count)])
        else:
            self.lut_list.append(lut.LUT())
            self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(1)])

        self.ui.combo_lut.setCurrentIndex(0)
        self.ui.combo_lut.setEnabled(self.ui.check_color_always.isChecked())

        if self.lut_list[0].bit_auto:
            self.ui.combo_bits.setCurrentText("Auto")
        else:
            self.ui.combo_bits.setCurrentText(self.lut_list[0].bit_mode)

        self.update_sliders()
        self.update_labels()

    def update_sliders (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        bit_range = current_lut.bit_range()

        self.ui.slider_cutoff_lower.setMinimum(bit_range[0])
        self.ui.slider_cutoff_lower.setMaximum(bit_range[1])
        self.ui.slider_cutoff_upper.setMinimum(bit_range[0])
        self.ui.slider_cutoff_upper.setMaximum(bit_range[1])

        self.ui.slider_cutoff_lower.setValue(current_lut.cutoff_lower)
        self.ui.slider_cutoff_upper.setValue(current_lut.cutoff_upper)

    def update_labels (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        bit_range = current_lut.bit_range()

        if current_lut.bit_mode == "Float":
            self.ui.label_cutoff_lower.setText("{0:e}".format(bit_range[0]))
            self.ui.label_cutoff_upper.setText("{0:e}".format(bit_range[1]))
            self.ui.label_slider_lower.setText("Lower limit: {0:e}".format(current_lut.cutoff_lower))
            self.ui.label_slider_upper.setText("Upper limit: {0:e}".format(current_lut.cutoff_upper))
        else:
            self.ui.label_cutoff_lower.setText(str(bit_range[0]))
            self.ui.label_cutoff_upper.setText(str(bit_range[1]))
            self.ui.label_slider_lower.setText("Lower limit: {0}".format(current_lut.cutoff_lower))
            self.ui.label_slider_upper.setText("Upper limit: {0}".format(current_lut.cutoff_upper))

    def adjust_slider_lower (self):
        self.ui.slider_cutoff_lower.setValue(min(self.ui.slider_cutoff_upper.value(), self.ui.slider_cutoff_lower.value()))
        self.update_current_lut()

    def adjust_slider_upper (self):
        self.ui.slider_cutoff_upper.setValue(max(self.ui.slider_cutoff_upper.value(), self.ui.slider_cutoff_lower.value()))
        self.update_current_lut()

    def update_current_lut (self):
        self.ui.check_auto_lut.setChecked(False)
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.cutoff_lower = self.ui.slider_cutoff_lower.value()
        current_lut.cutoff_upper = self.ui.slider_cutoff_upper.value()
        current_lut.lut_invert = self.ui.check_invert_lut.isChecked()
        current_lut.lut_name = self.ui.combo_lut.currentText()
        current_lut.bit_auto = (self.ui.combo_bits == "Auto")
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
        percent = self.ui.dspin_auto_cutoff.value()
        current_lut.bit_auto = True
        current_lut.cutoff_lower = np.percentile(image, percent)
        current_lut.cutoff_upper = np.percentile(image, 100 - percent)
        current_lut.lut_invert = self.ui.check_invert_lut.isChecked()
        current_lut.lut_name = self.ui.combo_lut.currentText()

        self.ui.slider_cutoff_lower.setValue(current_lut.cutoff_lower)
        self.ui.slider_cutoff_upper.setValue(current_lut.cutoff_upper)

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
        
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        self.ui.combo_lut.setCurrentText(current_lut.lut_name)
        if current_lut.bit_auto:
            self.ui.combo_bits.setCurrentText("Auto")
        else:
            self.ui.combo_bits.setCurrentText(current_lut.bit_mode)

        self.update_sliders()
        self.update_labels()

    def update_lut_view (self, image_lut, pixel_values = None):
        image_lut = self.lut_list[self.ui.combo_lut.currentIndex()]

    def current_channel (self):
        return self.ui.combo_channel.currentIndex()

    def color_always (self):
        return self.ui.check_color_always.isChecked()

    def is_composite (self):
        return self.ui.check_composite.isChecked()
    
    def is_auto_lut (self):
        return self.ui.check_auto_lut.isChecked()

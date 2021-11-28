#!/usr/bin/env python

import sys
import numpy as np
from image import lut

class LutPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.ui.combo_lut.addItems([item for item in lut.lut_dict])
        self.ui.combo_bits.addItems(["Auto"] + [item for item in lut.bit_dict])

    def init_widgets (self, stack = None):
        self.lut_list = []
        self.ui.combo_lut.setEnabled(True)
        self.ui.combo_channel.clear()

        if stack is not None:
            self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(stack.c_count)])
            for channel in range(stack.c_count):
                lut_name = lut.lut_names[channel % len(lut.lut_names)]
                image_lut = lut.LUT(lut_name = lut_name, pixel_values = stack.image_array[:, channel], bit_auto = True)
                self.lut_list.append(image_lut)

        else:
            self.lut_list.append(lut.LUT())

        self.ui.combo_lut.setCurrentText(self.lut_list[0].lut_name)
        self.ui.combo_lut.setEnabled(self.ui.check_color_always.isChecked())

        if self.lut_list[0].bit_auto:
            self.ui.combo_bits.setCurrentText("Auto")
        else:
            self.ui.combo_bits.setCurrentText(self.lut_list[0].bit_mode)

        self.update_sliders()

    def update_sliders (self):
        current_lut = self.lut_list[self.ui.combo_lut.currentIndex()]

        bit_range = current_lut.bit_range()
        self.ui.slider_cutoff_lower.setMinimum(bit_range[0])
        self.ui.slider_cutoff_lower.setMaximum(bit_range[1])
        self.ui.slider_cutoff_upper.setMinimum(bit_range[0])
        self.ui.slider_cutoff_upper.setMaximum(bit_range[1])

        self.ui.slider_cutoff_lower.setValue(current_lut.cutoff_lower)
        self.ui.slider_cutoff_upper.setValue(current_lut.cutoff_upper)

        if current_lut.bit_mode == "Float":
            self.ui.label_cutoff_lower.setText("{0:e}".format(bit_range[0]))
            self.ui.label_cutoff_upper.setText("{0:e}".format(bit_range[1]))
        else:
            self.ui.label_cutoff_lower.setText(str(bit_range[0]))
            self.ui.label_cutoff_upper.setText(str(bit_range[1]))

    def update_slider_lower (self):
        self.ui.slider_cutoff_lower.setValue(min(self.ui.slider_cutoff_upper.value(), self.ui.slider_cutoff_lower.value()))

    def update_slider_upper (self):
        self.ui.slider_cutoff_upper.setValue(max(self.ui.slider_cutoff_upper.value(), self.ui.slider_cutoff_lower.value()))

    def update_lut_view (self, image_lut, pixel_values = None):
        image_lut = self.lut_list[self.ui.combo_lut.currentIndex()]

    def current_channel (self):
        return self.ui.combo_lut.currentIndex()
    
    def is_composite (self):
        return self.ui.check_composite.isChecked()
    

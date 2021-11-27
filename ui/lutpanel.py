#!/usr/bin/env python

import sys
import numpy as np
from image import lut

class LutPanel:
    def __init__ (self, ui):
        self.ui = ui
        self.ui.combo_lut.addItems([item for item in lut.lut_dict])
        self.ui.combo_bits.addItems([item for item in lut.bit_dict])

    def init_widgets (self, stack = None):
        self.lut_list = []
        self.ui.combo_lut.setEnabled(True)
        self.ui.combo_channel.clear()

        if stack is not None:
            self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(stack.c_count)])
            for channel in range(stack.c_count):
                lut_name = lut.lut_dict[lut.lut_names[channel % len(lut.lut_names)]]
                image_lut = lut.LUT(lut_name = lut_name, pixel_values = stack.image_array[:, channel])
                self.lut_list.append(image_lut)

            if stack.c_count > 1 and self.ui.check_composite.value():
                self.ui.combo_lut.setCurrentText(self.lut_list[0].lut_name)
            else:
                self.ui.combo_lut.setCurrentText("Gray")
                self.ui.combo_lut.setEnabled(False)
            
            self.ui.combo_bits.setCurrentText(self.lut_list[0].bit_mode)
        else:
            self.lut_list.append(lut.LUT())

        self.set_sliders(self.lut_list[0])

    def set_sliders (self, image_lut):
        if image_lut.bit_mode == "Float":
            self.ui.slider_upper.setMinimum(image_lut.lower_limit)
            self.ui.slider_upper.setMaximum(image_lut.upper_limit)
            self.ui.slider_upper.setMinimum(image_lut.lower_limit)
            self.ui.slider_upper.setMaximum(image_lut.upper_limit)
        else:
            self.ui.slider_upper.setMinimum(lut.bit_dict[image_lut.bit_mode][0])
            self.ui.slider_upper.setMaximum(lut.bit_dict[image_lut.bit_mode][1])
            self.ui.slider_upper.setMinimum(lut.bit_dict[image_lut.bit_mode][0])
            self.ui.slider_upper.setMaximum(lut.bit_dict[image_lut.bit_mode][1])



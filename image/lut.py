#!/usr/bin/env python

import sys
import numpy as np

lut_dict = {}
lut_dict["Red"]     = [255,   0,   0]
lut_dict["Green"]   = [  0, 255,   0]
lut_dict["Blue"]    = [  0,   0, 255]
lut_dict["Magenta"] = [255,   0, 255]
lut_dict["Yellow"]  = [255, 255,   0]
lut_dict["Cyan"]    = [  0, 255, 255]
lut_dict["Gray"]    = [255, 255, 255]

lut_names = list(lut_dict.keys())

bit_dict = {}
bit_dict["Float"]    = [sys.float_info.min, sys.float_info.max]
bit_dict["INT-32+"]  = [0, np.iinfo(np.int32).max]
bit_dict["INT-16+"]  = [0, np.iinfo(np.uint16).max]
bit_dict["INT-8+"]  = [0, np.iinfo(np.uint8).max]
bit_dict["INT-32"]  = [np.iinfo(np.int32).min, np.iinfo(np.int32).max]
bit_dict["INT-16"]  = [np.iinfo(np.int16).min, np.iinfo(np.int16).max]
bit_dict["INT-8"]  = [np.iinfo(np.int8).min, np.iinfo(np.int8).max]
bit_names = list(bit_dict.keys())

class LUT:
    def __init__ (self, lut_name = None, pixel_values = None, lut_invert = False, bit_auto = False):
        if lut_name is None:
            self.lut_name = "Gray"
        else:
            self.lut_name = lut_name
        
        if pixel_values is None:
            self.bit_mode = "INT-16+"
            self.pixel_lower = bit_dict[self.bit_mode][0]
            self.pixel_upper = bit_dict[self.bit_mode][1]
        else:
            self.set_bit_mode(pixel_values)
            self.pixel_lower = np.min(pixel_values)
            self.pixel_upper = np.max(pixel_values)
            self.cutoff_lower = self.pixel_lower
            self.cutoff_upper = self.pixel_upper

        self.init_bit_mode = self.bit_mode[:]
        self.cutoff_lower = self.pixel_lower
        self.cutoff_upper = self.pixel_upper
        self.bit_auto = bit_auto
        self.lut_invert = lut_invert

    def set_bit_mode (self, pixel_values):
        max_value = pixel_values.max()
        min_value = pixel_values.min()

        if pixel_values.dtype.kind == 'i' or pixel_values.dtype.kind == 'u':
            if min_value >= 0:
                if max_value > np.iinfo(np.int32).max:
                    self.bit_mode = "Float"
                elif max_value > np.iinfo(np.uint16).max:
                    self.bit_mode = "INT-32+"
                elif max_value > np.iinfo(np.uint8).max:
                    self.bit_mode = "INT-16+"
                else:
                    self.bit_mode = "INT-8+"
            else:
                if max_value > np.iinfo(np.int32).max or min_value < np.iinfo(np.int32).min:
                    self.bit_mode = "Float"
                elif max_value > np.iinfo(np.int16).max or min_value < np.iinfo(np.int16).min:
                    self.bit_mode = "INT-32"
                elif max_value > np.iinfo(np.int8).max or min_value < np.iinfo(np.int8).min:
                    self.bit_mode = "INT-16"
                else:
                    self.bit_mode = "INT-8"
        else:
            self.bit_mode = "Float"

    def bit_range (self):
        if self.bit_auto == False and self.bit_mode != "Float":
            return bit_dict[self.bit_mode]

        lower_limit = max(self.pixel_lower, bit_dict[self.bit_mode][0])
        upper_limit = min(self.pixel_upper, bit_dict[self.bit_mode][1])

        return [lower_limit, upper_limit]

    def reset_bits (self):
        self.bit_mode = self.init_bit_mode[:]

    def apply_lut_float (self, image):
        image = image.astype(float)

        if np.isclose(self.cutoff_lower, self.cutoff_upper):
            image = 0.0
        else:
            image = (image - self.cutoff_lower) / (self.cutoff_upper - self.cutoff_lower)
            image = np.clip(image, 0.0, 1.0)

        if self.lut_invert:
            image = 1.0 - image

        return image

    def apply_lut_gray (self, image):
        return (self.apply_lut_float(image) * 255.0).astype(np.uint8)

    def apply_lut_rgb (self, image):
        max_values = lut_dict[self.lut_name]
        return [(max_value * self.apply_lut_float(image)).astype(np.uint8) for max_value in max_values]

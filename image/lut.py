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
bit_dict["UINT-32"]  = [np.iinfo(np.uint32).min, np.iinfo(np.uint32).max]
bit_dict["UINT-16"]  = [np.iinfo(np.uint16).min, np.iinfo(np.uint16).max]
bit_dict["UINT-8"]  = [np.iinfo(np.uint8).min, np.iinfo(np.uint8).max]
bit_dict["INT-32"]  = [np.iinfo(np.int32).min, np.iinfo(np.int32).max]
bit_dict["INT-16"]  = [np.iinfo(np.int16).min, np.iinfo(np.int16).max]
bit_dict["INT-8"]  = [np.iinfo(np.int8).min, np.iinfo(np.int8).max]
bit_names = list(bit_dict.keys())

class LUT:
    def __init__ (self, lut_name = None, pixel_values = None, bit_auto = False):
        if lut_name is None:
            self.lut_name = "Gray"
        else:
            self.lut_name = lut_name
        
        if pixel_values is None:
            self.bit_mode = "UINT-16"
            self.pixel_lower = bit_dict[self.bit_mode][0]
            self.pixel_upper = bit_dict[self.bit_mode][1]
        else:
            self.set_bit_mode(pixel_values)
            self.pixel_lower = np.min(pixel_values)
            self.pixel_upper = np.max(pixel_values)

        self.cutoff_lower = self.pixel_lower
        self.cutoff_upper = self.pixel_upper
        self.bit_auto = bit_auto

    def set_bit_mode (self, pixel_values):
        max_value = pixel_values.max()
        min_value = pixel_values.min()

        if pixel_values.dtype.kind == 'i' or pixel_values.dtype.kind == 'u':
            if min_value >= 0:
                if max_value > np.iinfo(np.uint32).max:
                    self.bit_mode = "Float"
                elif max_value > np.iinfo(np.uint16).max:
                    self.bit_mode = "UINT-32"
                elif max_value > np.iinfo(np.uint8).max:
                    self.bit_mode = "UINT-16"
                else:
                    self.bit_mode = "UINT-8"
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

    def lut_func (self, name):
        max_values = lut_dict[name]

        def matrix_to_rgb (matrix, lower, upper):
            ratio = (matrix - lower) / (upper - lower)
            matrix_r = (ratio * max_values[0]).astype(np.uint8)
            matrix_g = (ratio * max_values[1]).astype(np.uint8)
            matrix_b = (ratio * max_values[2]).astype(np.uint8)
            return np.stack((matrix_r, matrix_g, matrix_b), axis = -1)

        return matrix_to_rgb


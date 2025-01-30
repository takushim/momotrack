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
bit_dict["Auto"]    = [sys.float_info.min, sys.float_info.max]
bit_dict["Float"]    = [sys.float_info.min, sys.float_info.max]
bit_dict["INT-32+"]  = [0, np.iinfo(np.int32).max] # Sliders cannot handle UINT-32
bit_dict["UINT-16"]  = [0, np.iinfo(np.uint16).max]
bit_dict["UINT-14"]  = [0, 0x3FFF]
bit_dict["UINT-12"]  = [0, 0xFFF]
bit_dict["UINT-10"]  = [0, 0x3FF]
bit_dict["UINT-8"]   = [0, np.iinfo(np.uint8).max]
bit_dict["INT-32"]   = [np.iinfo(np.int32).min, np.iinfo(np.int32).max]
bit_dict["INT-16"]   = [np.iinfo(np.int16).min, np.iinfo(np.int16).max]
bit_dict["INT-14"]   = [-0x4000, 0x3FFF]
bit_dict["INT-12"]   = [-0x1000, 0xFFF]
bit_dict["INT-10"]   = [-0x400, 0x3FF]
bit_dict["INT-8"]    = [np.iinfo(np.int8).min, np.iinfo(np.int8).max]
bit_names = list(bit_dict.keys())

class LUT:
    def __init__ (self, lut_name = None, pixel_values = None):
        self.load_settings()
        if lut_name in lut_dict.keys():
            self.lut_name = lut_name
        self.reset_lut_range(pixel_values)

    def load_settings (self, settings = {}):
        self.lut_name = settings.get('lut_name', 'Gray')
        self.bit_mode = settings.get('bit_mode', 'UINT-16')
        self.lut_lower = settings.get('lut_lower', 0)
        self.lut_upper = settings.get('lut_upper', 0xffff)
        self.auto_lut = settings.get('auto_lut', False)
        self.auto_cutoff = settings.get('auto_cutoff', 0.0)
        self.lut_invert = settings.get('lut_invert', False)

        # necessary to return the lut range without the original image
        self.lut_min = self.lut_lower
        self.lut_max = self.lut_upper

    def reset_lut_range (self, pixel_values = None):
        self.load_settings(settings = {'lut_name': self.lut_name, 'lut_invert': self.lut_invert})
        if pixel_values is not None:
            self.optimize_bit_mode(pixel_values)
            self.set_range_by_image(pixel_values)
        self.lut_min = self.lut_lower
        self.lut_max = self.lut_upper

    def archive_settings (self):
        settings = {'lut_name': self.lut_name,
                    'bit_mode': self.bit_mode,
                    'lut_lower': self.lut_lower,
                    'lut_upper': self.lut_upper,
                    'auto_lut': self.auto_lut,
                    'auto_cutoff': self.auto_cutoff,
                    'lut_invert': self.lut_invert}
        return settings

    def optimize_bit_mode (self, pixel_values):
        max_value = pixel_values.max()
        min_value = pixel_values.min()

        if pixel_values.dtype.kind == 'i' or pixel_values.dtype.kind == 'u':
            if min_value < 0:
                cand_dict = {name: bit_range for name, bit_range in bit_dict.items() if bit_range[0] < 0}
            else:
                cand_dict = {name: bit_range for name, bit_range in bit_dict.items() if bit_range[0] >= 0}

            self.bit_mode = "Float"
            for name, bit_range in cand_dict.items():
                if max_value > bit_range[1]:
                    break
                else:
                    self.bit_mode = name
        else:
            self.bit_mode = "Float"

    def lut_range (self):
        if self.bit_mode == "Auto":
            return [int(self.lut_min), int(self.lut_max)]
        elif self.bit_mode == "Float":
            return [float(self.lut_min), float(self.lut_max)]

        return bit_dict[self.bit_mode]

    def set_range_by_image (self, pixel_values, percentile = 0):
        self.auto_lut = True
        self.auto_cutoff = percentile
        if self.bit_mode == "Float":
            self.lut_lower = np.percentile(pixel_values, percentile)
            self.lut_upper = np.percentile(pixel_values, 100 - percentile)
        else:
            self.lut_lower = int(np.percentile(pixel_values, percentile))
            self.lut_upper = int(np.percentile(pixel_values, 100 - percentile))

    def apply_lut_float (self, image):
        image = image.astype(float)

        if np.isclose(self.lut_lower, self.lut_upper):
            image[:] = 0.0
        else:
            image = (image - self.lut_lower) / (self.lut_upper - self.lut_lower)
            image = np.clip(image, 0.0, 1.0)

        if self.lut_invert:
            image = 1.0 - image

        return image

    def apply_lut_gray (self, image):
        return (self.apply_lut_float(image) * 255.0).astype(np.uint8)

    def apply_lut_rgb (self, image):
        max_values = lut_dict[self.lut_name]
        return [(max_value * self.apply_lut_float(image)).astype(np.uint8) for max_value in max_values]

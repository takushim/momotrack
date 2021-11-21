#!/usr/bin/env python

import sys
import numpy as np

lut_dict = {}
lut_dict["Gray"]    = [255, 255, 255]
lut_dict["Red"]     = [255,   0,   0]
lut_dict["Green"]   = [  0, 255,   0]
lut_dict["Blue"]    = [  0,   0, 255]
lut_dict["Magenta"] = [255,   0, 255]
lut_dict["Yellow"]  = [255, 255,   0]
lut_dict["Cyan"]    = [  0, 255, 255]

lut_names = lut_dict.keys()

def find_lut (name):
    try:
        lower_list = [lut_name.lower() for lut_name in lut_names]
        name = lut_names[lower_list.index(name.lower())]
    except ValueError:
        name = None

    return name

def lut_func (name):
    max_values = lut_dict[find_lut(name)]

    def matrix_to_rgb (matrix, lower, upper):
        ratio = (matrix - lower) / (upper - lower)
        matrix_r = (ratio * max_values[0]).astype(np.uint8)
        matrix_g = (ratio * max_values[1]).astype(np.uint8)
        matrix_b = (ratio * max_values[2]).astype(np.uint8)
        return np.stack((matrix_r, matrix_g, matrix_b), axis = -1)

    return matrix_to_rgb


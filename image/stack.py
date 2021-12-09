#!/usr/bin/env python

import sys, tifffile
import numpy as np
from pathlib import Path

pixels_um = [0.1625, 0.1625]
z_step_um = 0.5
file_types = {"TIFF Image": ["*.tif", "*.tiff", "*.stk"]}

class Stack:
    def __init__ (self, filename = None, keep_color = False):
        self.pixels_um = pixels_um
        self.z_step_um = z_step_um
        self.filename = filename

        if self.filename is None:
            self.z_count = 1
            self.t_count = 1
            self.c_count = 1
            self.height = 256
            self.width = 256
            self.axes = 'TCZYX'
            self.colored = False
            self.filename = None
            self.image_array = np.zeros((self.t_count, self.c_count, self.z_count, self.height, self.width), dtype = np.uint16)
        else:
            self.read_image(keep_color = keep_color)

    def read_image (self, keep_color = False):
        # read TIFF file (assumes TZ(C)YX(S) order)
        with tifffile.TiffFile(self.filename) as tiff:
            axes = tiff.series[0].axes
            self.image_array = tiff.asarray(series = 0)
            self.read_metadata(tiff)

        if 'T' not in axes:
            self.image_array = self.image_array[np.newaxis]
        if 'Z' not in axes:
            self.image_array = self.image_array[:, np.newaxis]
        if 'C' not in axes:
            self.image_array = self.image_array[:, :, np.newaxis]

        # swap Z and C axes
        self.image_array = self.image_array.swapaxes(1, 2)

        self.t_count = self.image_array.shape[0]
        self.c_count = self.image_array.shape[1]
        self.z_count = self.image_array.shape[2]
        self.height = self.image_array.shape[3]
        self.width = self.image_array.shape[4]

        if 'S' in axes:
            if keep_color:
                self.axes = 'TZCYXS'
                self.colored = True
                self.s_count = self.image_array.shape[5]
            else:
                image_list = [self.image_array[..., index] for index in range(self.image_array.shape[-1])]
                self.image_array = np.stack(image_list, axis = 1)
                self.c_count = self.image_array.shape[1]
                self.colored = False
        else:
            self.axes = 'TCZYX'
            self.colored = False

    def read_metadata (self, tiff):
        self.pixels_um = pixels_um
        self.z_step_um = z_step_um

        if 'XResolution' in tiff.pages[0].tags:
            values = tiff.pages[0].tags['XResolution'].value
            self.pixels_um[0] = float(values[1]) / float(values[0])

        if 'YResolution' in tiff.pages[0].tags:
            values = tiff.pages[0].tags['YResolution'].value
            self.pixels_um[1] = float(values[1]) / float(values[0])

        if 'ImageDescription' in tiff.pages[0].tags:
            if tiff.imagej_metadata is not None:
                if 'spacing' in tiff.imagej_metadata:
                    self.z_step_um = tiff.imagej_metadata['spacing']
            elif tiff.ome_metadata is not None:
                if 'spacing' in tiff.ome_metadata:
                    self.z_step_um = tiff.ome_metadata['spacing']


#!/usr/bin/env python

import numpy as np
from ndimage import gaussian_laplace
from skimage.feature import peak_local_max

class Gaussian8:
    def __init__ (self):
        self.laplace = 2.0 # Diameter of Spots
        self.min_distance = 1 # Pixel area (int) to find local max (usually 1)
        self.threshold_abs = 0.006 # Threshold to find local max
        self.max_diameter = 10.0
        self.dup_threshold = 3.0
        self.columns = ['total_index', 'plane', 'index', 'x', 'y', 'diameter', 'intensity', 'fit_error', 'chi_square']
        self.image_clip_min = 0.0
        self.image_clip_max = np.iinfo(np.int32).max

    def set_image_clip (self, image_array):
        self.image_clip_min = np.percentile(image_array, 0.1)
        self.image_clip_max = np.percentile(image_array, 99.9)

    def standardize_and_filter_image (self, float_image):
        float_image = - (float_image - np.max(float_image)) / np.ptp(float_image)
        return gaussian_laplace(float_image, self.laplace)

    def gaussian_fitting (self, input_image, float_image):
        # Find local max at 1-pixel resolution (order: [y, x])
        xy = peak_local_max(float_image, min_distance = self.min_distance,\
                            threshold_abs = self.threshold_abs, exclude_border = True)

        # Calculate subpixel correction (x = xy[:,1], y = xy[:,0])
        c10 = ( - np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) - np.log(float_image[xy[:,0], xy[:,1] - 1]) \
                - np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) + np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) \
                + np.log(float_image[xy[:,0], xy[:,1] + 1]) + np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) ) / 6
        c01 = ( - np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) - np.log(float_image[xy[:,0] - 1, xy[:,1]]) \
                - np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) + np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) \
                + np.log(float_image[xy[:,0] + 1, xy[:,1]]) + np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) ) / 6
        c20 = (   np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) + np.log(float_image[xy[:,0], xy[:,1] - 1]) \
                + np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) - 2 * np.log(float_image[xy[:,0] - 1,xy[:,1]]) \
                - 2 * np.log(float_image[xy[:,0], xy[:,1]]) - 2 * np.log(float_image[xy[:,0] + 1, xy[:,1]]) \
                + np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) + np.log(float_image[xy[:,0], xy[:,1] + 1]) \
                + np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) ) / 6
        c02 = (   np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) + np.log(float_image[xy[:,0] - 1,xy[:,1]]) \
                + np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) - 2 * np.log(float_image[xy[:,0], xy[:,1] - 1]) \
                - 2 * np.log(float_image[xy[:,0], xy[:,1]]) - 2 * np.log(float_image[xy[:,0], xy[:,1] + 1]) \
                + np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) + np.log(float_image[xy[:,0] + 1,xy[:,1]]) \
                + np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) ) / 6
        c00 = ( - np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) + 2 * np.log(float_image[xy[:,0], xy[:,1] - 1]) \
                - np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) + 2 * np.log(float_image[xy[:,0] - 1,xy[:,1]]) \
                + 5 * np.log(float_image[xy[:,0], xy[:,1]]) + 2 * np.log(float_image[xy[:,0] + 1, xy[:,1]]) \
                - np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) + 2 * np.log(float_image[xy[:,0], xy[:,1] + 1]) \
                - np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) ) / 9

        fit_error = ( c00 - c10 + c20 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) )**2 \
            + ( c00 - c10 + c20 - np.log(float_image[xy[:,0], xy[:,1] - 1]) )**2 \
            + ( c00 - c10 + c20 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) )**2 \
            + ( c00 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1]]) )**2 \
            + ( c00 - np.log(float_image[xy[:,0], xy[:,1]]) )**2 \
            + ( c00 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1]]) )**2 \
            + ( c00 + c10 + c20 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) )**2 \
            + ( c00 + c10 + c20 - np.log(float_image[xy[:,0], xy[:,1] + 1]) )**2 \
            + ( c00 + c10 + c20 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) )**2

        chi_square = ( c00 - c10 + c20 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1] - 1]) )**2 / np.abs(np.log(float_image[xy[:,0] - 1, xy[:,1] - 1])) \
                   + ( c00 - c10 + c20 - np.log(float_image[xy[:,0], xy[:,1] - 1]) )**2 / np.abs(np.log(float_image[xy[:,0], xy[:,1] - 1])) \
                   + ( c00 - c10 + c20 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1] - 1]) )**2  / np.abs(np.log(float_image[xy[:,0] + 1, xy[:,1] - 1])) \
                   + ( c00 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1]]) )**2  / np.abs(np.log(float_image[xy[:,0] - 1, xy[:,1]])) \
                   + ( c00 - np.log(float_image[xy[:,0], xy[:,1]]) )**2  / np.abs(np.log(float_image[xy[:,0], xy[:,1]])) \
                   + ( c00 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1]]) )**2  / np.abs(np.log(float_image[xy[:,0] + 1, xy[:,1]])) \
                   + ( c00 + c10 + c20 - c01 + c02 - np.log(float_image[xy[:,0] - 1, xy[:,1] + 1]) )**2  / np.abs(np.log(float_image[xy[:,0] - 1, xy[:,1] + 1])) \
                   + ( c00 + c10 + c20 - np.log(float_image[xy[:,0], xy[:,1] + 1]) )**2  / np.abs(np.log(float_image[xy[:,0], xy[:,1] + 1])) \
                   + ( c00 + c10 + c20 + c01 + c02 - np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]) )**2  / np.abs(np.log(float_image[xy[:,0] + 1, xy[:,1] + 1]))

        x = xy[:,1] - 0.5 * (c10/c20)
        y = xy[:,0] - 0.5 * (c01/c02)
        diameter = 2 * np.sqrt(- (0.5/c20 + 0.5/c02) / 2)
        intensity = input_image[xy[:,0], xy[:,1]]

        # make result dictionary
        result_dict = {'x': x, 'y': y, 'fit_error': fit_error, 'chi_square': chi_square, 'diameter': diameter, 'intensity': intensity}
        error_dict = {}

        # omit spots of abnormal subpixel correction (this should be run first of all)
        indexes = np.ones(len(result_dict['x']), dtype=bool)
        indexes = indexes & ((0.5 * (c10/c20)) < 1)
        indexes = indexes & ((0.5 * (c01/c02)) < 1)
        error_dict['large_subpixel_shift'] = len(result_dict['x']) - np.sum(indexes)
        result_dict = {k: result_dict[k][indexes] for k in result_dict}

        # omit nan spots
        indexes = np.ones(len(result_dict['x']), dtype=bool)
        indexes = indexes & (result_dict['x'] >= 0) & (result_dict['x'] <= float_image.shape[1])
        indexes = indexes & (result_dict['y'] >= 0) & (result_dict['y'] <= float_image.shape[0])
        error_dict['nan_coordinate'] = len(result_dict['x']) - np.sum(indexes)
        result_dict = {k: result_dict[k][indexes] for k in result_dict}

        # omit spots of large diameter
        indexes = np.ones(len(result_dict['x']), dtype=bool)
        indexes = indexes & (result_dict['diameter'] <= self.max_diameter)
        error_dict['large_diameter'] = len(result_dict['x']) - np.sum(indexes)
        result_dict = {k: result_dict[k][indexes] for k in result_dict}

    def fitting_image_array (self, input_image):
        np.seterr(divide='ignore', invalid='ignore')

        # get float image anf filter
        float_image = np.array(input_image, 'f')
        float_image = self.clip_array(float_image)
        float_image = self.standardize_and_filter_image(float_image)

        # fitting
        result, error = self.gaussian_fitting(input_image, float_image)

        # report error
        print("Dropped spots: %s" % (str(error)))

        # Make Pandas dataframe
        length = max([len(item) for item in result.values()])
        result.update({'plane': np.full(length, 0), 'index': np.arange(length)})
        spot_table = self.convert_to_pandas(result)

        return spot_table


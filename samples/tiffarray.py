#!/usr/bin/env python

import numpy as np
import argparse, tifffile
from pprint import pprint
from pathlib import Path

# default values
input_filename = None
output_filename = None
output_suffix = "_array.txt"

# parse arguments
parser = argparse.ArgumentParser(description='Convert a TIFF image to an array', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-o', '--output-file', default = output_filename, \
                    help='output image filename. [basename]{0} by default'.format(output_suffix))
parser.add_argument('input_file', default = input_filename, \
                    help='input (multipage) TIFF file')
args = parser.parse_args()

# set arguments
input_filename = args.input_file
if args.output_file is None:
    output_filename = Path(input_filename).stem + output_suffix
else:
    output_filename = args.output_file

# read and output file
input_image = tifffile.imread(input_filename)

with open(output_filename, mode = 'w') as f:
    pprint(input_image, f)

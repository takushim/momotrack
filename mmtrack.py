#!/usr/bin/env python

import sys, argparse
from PySide6.QtWidgets import QApplication
from ui import mainwindow
from image import path

# default parameters
input_filename = None
record_filename = None
record_suffix = '_record.txt'

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--record-file', default = record_filename,
                    help='JSON file to record tracking data. [basename]_[suffix].json by default.')

parser.add_argument('input_file', nargs = '?', default = input_filename, \
                    help='input TIFF file')

args, unparsed_args = parser.parse_known_args()

# set values
input_filename = args.input_file
record_filename = args.record_file
if input_filename is not None and record_filename is None:
    record_filename = path.with_suffix(input_filename, record_suffix)

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)
window = mainwindow.MainWindow(image_filename = input_filename, record_filename = record_filename)
window.show()
sys.exit(app.exec())

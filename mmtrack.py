#!/usr/bin/env python

import sys, argparse
from PySide6.QtWidgets import QApplication
from ui import mainwindow

# default parameters
image_filename = None
record_filename = None

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--record-file', default = record_filename,
                    help='JSON file to record tracking data. [basename]_[suffix].json by default.')

parser.add_argument('image_file', nargs = '?', default = image_filename, \
                    help='TIFF file to analyze')

args, unparsed_args = parser.parse_known_args()

# set values
image_filename = args.image_file
record_filename = args.record_file

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)
window = mainwindow.MainWindow(image_filename = image_filename, record_filename = record_filename)
window.show()
sys.exit(app.exec())

#!/usr/bin/env python

import sys, argparse
from PySide6.QtWidgets import QApplication
from ui import mainwindow
from etc import imagestack

# default parameters
input_filename = None
tracks_filename = None
tracks_suffix = '_track.txt'
channel = 0
z_index = 0

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--tracks-file', default = tracks_filename,
                    help='file to record tracking data. [basename]{0} by default.'.format(tracks_suffix))

parser.add_argument('-c', '--channel', type = int, default = channel, \
                    help='channel to process.')

parser.add_argument('-z', '--z-index', type = int, default = z_index, \
                    help='z-index to process.')

parser.add_argument('input_file', nargs = '?', default = input_filename, \
                    help='input TIFF file')

args, unparsed_args = parser.parse_known_args()

# set values
input_filename = args.input_file
channel = args.channel
z_index = args.z_index
tracks_filename = args.tracks_file
if input_filename is not None and tracks_filename is None:
    tracks_filename = imagestack.with_suffix(input_filename, tracks_suffix)

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)
window = mainwindow.MainWindow()
window.show()
sys.exit(app.exec())

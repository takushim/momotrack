#!/usr/bin/env python

import sys, argparse
from PySide6.QtWidgets import QApplication
from ui import mainwindow

# default parameters
image_filenames = None
records_filenames = None
plugin_names = None

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-p', '--plugin-name', default = plugin_names, action = 'append', \
                    help='Plugin loaded by default. Can be used multiple times.')

parser.add_argument('-f', '--records-file', default = records_filenames, action = 'append', \
                    help='JSON file recording data. Can be used multiple times.')

parser.add_argument('image_file', nargs = '*', default = image_filenames, \
                    help='TIFF files to analyze')

args, unparsed_args = parser.parse_known_args()

# set values
image_filenames = args.image_file
records_filenames = [] if args.records_file is None else args.records_file
plugin_names = [] if args.plugin_name is None else args.plugin_name

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)

# open the main window
window_x = 0
window_y = 0

for index in range(max(1, len(image_filenames))):
    image_filename = image_filenames[index] if len(image_filenames) > index else None
    plugin_name = plugin_names[index] if len(plugin_names) > index else None
    records_filename = records_filenames[index] if len(records_filenames) > index else None

    window = mainwindow.MainWindow(image_filename = image_filename, \
                                   records_filename = records_filename, \
                                   plugin_name = plugin_name)
    window.resize_best()

    window_x, window_y = window.next_window_position(window_x, window_y)
    window.move(window_x, window_y)
    window.show()
    window.zoom_best()

sys.exit(app.exec())

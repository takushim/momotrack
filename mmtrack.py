#!/usr/bin/env python

import sys, argparse
from PySide6.QtWidgets import QApplication
from ui import mainwindow

# default parameters
image_filename = None
records_filename = None
plugin_name = None

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-p', '--plugin-name', default = records_filename,
                    help='Plugin loaded at startup.')

parser.add_argument('-f', '--records-file', default = records_filename,
                    help='JSON file to record data. [basename]_[suffix].json by default.')

parser.add_argument('image_file', nargs = '?', default = image_filename, \
                    help='TIFF files to analyze')

args, unparsed_args = parser.parse_known_args()

# set values
image_filename = args.image_file
records_filename = args.records_file
plugin_name = args.plugin_name

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)

# open the main window
window = mainwindow.MainWindow(image_filename = image_filename, records_filename = records_filename, plugin_name = plugin_name)
window.resize_best()

screen_size = window.screen().availableSize()
window_x = (screen_size.width() - window.width()) // 2
window_y = (screen_size.height() - window.height()) // 2
window.move(window_x, window_y)

window.show()
window.zoom_best()

sys.exit(app.exec())

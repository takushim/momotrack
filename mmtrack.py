#!/usr/bin/env python

import subprocess
import sys, argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QProcess, QObject
import image
from ui import mainwindow

# default parameters
image_filenames = None
records_filenames = None
plugin_names = None
window_position = None
window_size = None

# parse arguments
parser = argparse.ArgumentParser(description='Object tracking system for 3D images.', \
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-p', '--plugin-name', default = plugin_names, action = 'append', \
                    help='Plugin loaded by default. Can be used multiple times.')

parser.add_argument('-f', '--records-file', default = records_filenames, action = 'append', \
                    help='JSON file recording data. Can be used multiple times.')

parser.add_argument('--window-position', nargs = 2, type = int, default = window_position, \
                    metavar = ('X', 'Y'), \
                    help='Position of the first window')

parser.add_argument('--window-size', nargs = 2, type = int, default = window_size, \
                    metavar = ('W', 'H'), \
                    help='Size of windows')

parser.add_argument('image_file', nargs = '*', default = image_filenames, \
                    help='TIFF files to analyze')

args, unparsed_args = parser.parse_known_args()

# set values
image_filenames = args.image_file
records_filenames = [] if args.records_file is None else args.records_file
plugin_names = [] if args.plugin_name is None else args.plugin_name
window_position = args.window_position
window_size = args.window_size

# start the Qt system
app = QApplication(sys.argv[:1] + unparsed_args)

# functions
def next_window_position (x, y):
    screen_size = QGuiApplication.primaryScreen().size()
    delta = int(screen_size.width() * 0.02)
    next_x = (x + delta) % (screen_size.width() // 2)
    next_y = (y + delta) % (screen_size.height() // 2)
    return next_x, next_y

def slot_open_mainwindow (image_list):
    if image_list is None:
        image_list = []

    window_x, window_y = next_window_position(0, 0)
    window_x, window_y = next_window_position(window_x, window_y)
    program = __file__
    for index in range(max(1, len(image_list))):
        filename = image_list[index] if len(image_list) > index else None
        commands = ["py", program, "--window-position", str(window_x), str(window_y)]
        if filename is not None:
            commands.append(filename)
        subprocess.run(commands)
        window_x, window_y = next_window_position(window_x, window_y)

# open the main window(s)
if window_position is None:
    window_x, window_y = next_window_position(0, 0)
else:
    window_x, window_y = window_position

for index in range(max(1, len(image_filenames))):
    image_filename = image_filenames[index] if len(image_filenames) > index else None
    plugin_name = plugin_names[index] if len(plugin_names) > index else None
    records_filename = records_filenames[index] if len(records_filenames) > index else None

    window = mainwindow.MainWindow(image_filename = image_filename, \
                                   records_filename = records_filename, \
                                   plugin_name = plugin_name)

    window.signal_open_new_image.connect(slot_open_mainwindow)
    window.resize_best()

    window.move(window_x, window_y)
    window_x, window_y = next_window_position(window_x, window_y)

    window.show()
    window.zoom_best()

sys.exit(app.exec())

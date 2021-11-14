#!/usr/bin/env python

import sys
from PySide6.QtWidgets import QApplication
from ui import mainwindow


app = QApplication(sys.argv)
main = mainwindow.MainWindow()
sys.exit(app.exec())

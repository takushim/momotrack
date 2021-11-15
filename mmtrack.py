#!/usr/bin/env python

import sys
from PySide6.QtWidgets import QApplication
from ui import mainwindow


app = QApplication(sys.argv)
main = mainwindow.MainWindow()
main.show()
sys.exit(app.exec())

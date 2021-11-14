#!/usr/bin/env python

from PyQt6.QtWidgets import QMainWindow, QAction

class MainWindow (QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle('Hello World!')
        #self.setGeometry(100,100,200,150)
        self.create_actions()
        self.create_menu()

    def create_menu (self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction("&Open image")
        filemenu.addAction("&Load spots")
        filemenu.addAction("&Save spots")
        filemenu.addAction("&Close spots")
        filemenu.addSeparator()
        filemenu.addAction("&Quit")
        helpmenu = menubar.addMenu("&Help")
        helpmenu.addAction("&About")

    def create_actions (self):
        self.action_about = QAction("&About", self)


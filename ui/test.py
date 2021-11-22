#!/usr/bin/env python

import sys
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QGraphicsScene
from PySide6.QtCore import QFile, QObject, SIGNAL
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QImage

class TestWindow (QMainWindow):
    def __init__ (self):
        super().__init__()
        self.load_ui()

    def load_ui (self):
        file = QFile("ui/test.ui")
        file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui)

        qimage = QImage("test/lena_std.tif")
        pixmap = QPixmap(qimage)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        self.ui.gview_image.setScene(scene)

        #QObject.connect(self.ui.gview_image, SIGNAL(), self.mousePressEvent)

    def mousePressEvent (self, event):
        pos = self.ui.gview_image.mapFromParent(event.pos()) - self.ui.centralwidget.pos()
        print(pos)


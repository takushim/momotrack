# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGraphicsView, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(400, 300))
        self.action_open_image = QAction(MainWindow)
        self.action_open_image.setObjectName(u"action_open_image")
        self.action_load_spots = QAction(MainWindow)
        self.action_load_spots.setObjectName(u"action_load_spots")
        self.action_save_spots = QAction(MainWindow)
        self.action_save_spots.setObjectName(u"action_save_spots")
        self.action_save_spots_as = QAction(MainWindow)
        self.action_save_spots_as.setObjectName(u"action_save_spots_as")
        self.action_save_spots_as.setShortcutVisibleInContextMenu(True)
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_zoom_in = QAction(MainWindow)
        self.action_zoom_in.setObjectName(u"action_zoom_in")
        self.action_zoom_out = QAction(MainWindow)
        self.action_zoom_out.setObjectName(u"action_zoom_out")
        self.action_reset_zoom = QAction(MainWindow)
        self.action_reset_zoom.setObjectName(u"action_reset_zoom")
        self.action_quick_help = QAction(MainWindow)
        self.action_quick_help.setObjectName(u"action_quick_help")
        self.action_about = QAction(MainWindow)
        self.action_about.setObjectName(u"action_about")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QSize(400, 300))
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hlayout_all = QHBoxLayout()
        self.hlayout_all.setObjectName(u"hlayout_all")
        self.hlayout_all.setSizeConstraint(QLayout.SetMaximumSize)
        self.vlayout_view = QVBoxLayout()
        self.vlayout_view.setObjectName(u"vlayout_view")
        self.vlayout_view.setSizeConstraint(QLayout.SetMaximumSize)
        self.view_image = QGraphicsView(self.centralwidget)
        self.view_image.setObjectName(u"view_image")
        self.view_image.setMinimumSize(QSize(400, 400))

        self.vlayout_view.addWidget(self.view_image)

        self.hlayout_slider_zstack = QHBoxLayout()
        self.hlayout_slider_zstack.setObjectName(u"hlayout_slider_zstack")
        self.hlayout_slider_zstack.setSizeConstraint(QLayout.SetMaximumSize)
        self.label_zstack = QLabel(self.centralwidget)
        self.label_zstack.setObjectName(u"label_zstack")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_zstack.sizePolicy().hasHeightForWidth())
        self.label_zstack.setSizePolicy(sizePolicy1)

        self.hlayout_slider_zstack.addWidget(self.label_zstack)

        self.slider_zstack = QSlider(self.centralwidget)
        self.slider_zstack.setObjectName(u"slider_zstack")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.slider_zstack.sizePolicy().hasHeightForWidth())
        self.slider_zstack.setSizePolicy(sizePolicy2)
        self.slider_zstack.setOrientation(Qt.Horizontal)

        self.hlayout_slider_zstack.addWidget(self.slider_zstack)


        self.vlayout_view.addLayout(self.hlayout_slider_zstack)

        self.hlayout_slider_time = QHBoxLayout()
        self.hlayout_slider_time.setObjectName(u"hlayout_slider_time")
        self.hlayout_slider_time.setSizeConstraint(QLayout.SetMaximumSize)
        self.label_time = QLabel(self.centralwidget)
        self.label_time.setObjectName(u"label_time")
        sizePolicy1.setHeightForWidth(self.label_time.sizePolicy().hasHeightForWidth())
        self.label_time.setSizePolicy(sizePolicy1)

        self.hlayout_slider_time.addWidget(self.label_time)

        self.slider_time = QSlider(self.centralwidget)
        self.slider_time.setObjectName(u"slider_time")
        sizePolicy2.setHeightForWidth(self.slider_time.sizePolicy().hasHeightForWidth())
        self.slider_time.setSizePolicy(sizePolicy2)
        self.slider_time.setOrientation(Qt.Horizontal)

        self.hlayout_slider_time.addWidget(self.slider_time)


        self.vlayout_view.addLayout(self.hlayout_slider_time)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_status = QLabel(self.centralwidget)
        self.label_status.setObjectName(u"label_status")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_status.sizePolicy().hasHeightForWidth())
        self.label_status.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.label_status)

        self.button_play = QPushButton(self.centralwidget)
        self.button_play.setObjectName(u"button_play")
        sizePolicy1.setHeightForWidth(self.button_play.sizePolicy().hasHeightForWidth())
        self.button_play.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.button_play)

        self.spin_fps = QSpinBox(self.centralwidget)
        self.spin_fps.setObjectName(u"spin_fps")
        sizePolicy1.setHeightForWidth(self.spin_fps.sizePolicy().hasHeightForWidth())
        self.spin_fps.setSizePolicy(sizePolicy1)
        self.spin_fps.setMinimum(1)
        self.spin_fps.setMaximum(100)
        self.spin_fps.setValue(10)

        self.horizontalLayout.addWidget(self.spin_fps)

        self.label_fps = QLabel(self.centralwidget)
        self.label_fps.setObjectName(u"label_fps")
        sizePolicy1.setHeightForWidth(self.label_fps.sizePolicy().hasHeightForWidth())
        self.label_fps.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.label_fps)


        self.vlayout_view.addLayout(self.horizontalLayout)


        self.hlayout_all.addLayout(self.vlayout_view)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.hlayout_all.addWidget(self.line)

        self.vlayout_panel = QVBoxLayout()
        self.vlayout_panel.setObjectName(u"vlayout_panel")
        self.vlayout_panel.setSizeConstraint(QLayout.SetMinimumSize)
        self.label_channel = QLabel(self.centralwidget)
        self.label_channel.setObjectName(u"label_channel")
        sizePolicy1.setHeightForWidth(self.label_channel.sizePolicy().hasHeightForWidth())
        self.label_channel.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.label_channel)

        self.combo_channel = QComboBox(self.centralwidget)
        self.combo_channel.setObjectName(u"combo_channel")
        sizePolicy1.setHeightForWidth(self.combo_channel.sizePolicy().hasHeightForWidth())
        self.combo_channel.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.combo_channel)

        self.combo_lut = QComboBox(self.centralwidget)
        self.combo_lut.setObjectName(u"combo_lut")
        sizePolicy1.setHeightForWidth(self.combo_lut.sizePolicy().hasHeightForWidth())
        self.combo_lut.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.combo_lut)

        self.check_hide_others = QCheckBox(self.centralwidget)
        self.check_hide_others.setObjectName(u"check_hide_others")
        sizePolicy1.setHeightForWidth(self.check_hide_others.sizePolicy().hasHeightForWidth())
        self.check_hide_others.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.check_hide_others)

        self.check_invert_lut = QCheckBox(self.centralwidget)
        self.check_invert_lut.setObjectName(u"check_invert_lut")
        sizePolicy1.setHeightForWidth(self.check_invert_lut.sizePolicy().hasHeightForWidth())
        self.check_invert_lut.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.check_invert_lut)

        self.combo_bits = QComboBox(self.centralwidget)
        self.combo_bits.setObjectName(u"combo_bits")
        sizePolicy1.setHeightForWidth(self.combo_bits.sizePolicy().hasHeightForWidth())
        self.combo_bits.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.combo_bits)

        self.view_lut = QGraphicsView(self.centralwidget)
        self.view_lut.setObjectName(u"view_lut")
        sizePolicy1.setHeightForWidth(self.view_lut.sizePolicy().hasHeightForWidth())
        self.view_lut.setSizePolicy(sizePolicy1)
        self.view_lut.setMinimumSize(QSize(120, 90))

        self.vlayout_panel.addWidget(self.view_lut)

        self.hlayout_lut_range = QHBoxLayout()
        self.hlayout_lut_range.setObjectName(u"hlayout_lut_range")
        self.label_lut_lower = QLabel(self.centralwidget)
        self.label_lut_lower.setObjectName(u"label_lut_lower")
        sizePolicy1.setHeightForWidth(self.label_lut_lower.sizePolicy().hasHeightForWidth())
        self.label_lut_lower.setSizePolicy(sizePolicy1)

        self.hlayout_lut_range.addWidget(self.label_lut_lower)

        self.label_lut_upper = QLabel(self.centralwidget)
        self.label_lut_upper.setObjectName(u"label_lut_upper")
        sizePolicy1.setHeightForWidth(self.label_lut_upper.sizePolicy().hasHeightForWidth())
        self.label_lut_upper.setSizePolicy(sizePolicy1)
        self.label_lut_upper.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.hlayout_lut_range.addWidget(self.label_lut_upper)


        self.vlayout_panel.addLayout(self.hlayout_lut_range)

        self.label_upper = QLabel(self.centralwidget)
        self.label_upper.setObjectName(u"label_upper")
        sizePolicy1.setHeightForWidth(self.label_upper.sizePolicy().hasHeightForWidth())
        self.label_upper.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.label_upper)

        self.slider_upper = QSlider(self.centralwidget)
        self.slider_upper.setObjectName(u"slider_upper")
        sizePolicy1.setHeightForWidth(self.slider_upper.sizePolicy().hasHeightForWidth())
        self.slider_upper.setSizePolicy(sizePolicy1)
        self.slider_upper.setOrientation(Qt.Horizontal)

        self.vlayout_panel.addWidget(self.slider_upper)

        self.label_lower = QLabel(self.centralwidget)
        self.label_lower.setObjectName(u"label_lower")
        sizePolicy1.setHeightForWidth(self.label_lower.sizePolicy().hasHeightForWidth())
        self.label_lower.setSizePolicy(sizePolicy1)

        self.vlayout_panel.addWidget(self.label_lower)

        self.slider_lower = QSlider(self.centralwidget)
        self.slider_lower.setObjectName(u"slider_lower")
        sizePolicy1.setHeightForWidth(self.slider_lower.sizePolicy().hasHeightForWidth())
        self.slider_lower.setSizePolicy(sizePolicy1)
        self.slider_lower.setOrientation(Qt.Horizontal)

        self.vlayout_panel.addWidget(self.slider_lower)

        self.hlayout_lut_set = QHBoxLayout()
        self.hlayout_lut_set.setObjectName(u"hlayout_lut_set")
        self.button_reset_lut = QPushButton(self.centralwidget)
        self.button_reset_lut.setObjectName(u"button_reset_lut")
        sizePolicy1.setHeightForWidth(self.button_reset_lut.sizePolicy().hasHeightForWidth())
        self.button_reset_lut.setSizePolicy(sizePolicy1)

        self.hlayout_lut_set.addWidget(self.button_reset_lut)

        self.button_auto_lut = QPushButton(self.centralwidget)
        self.button_auto_lut.setObjectName(u"button_auto_lut")
        sizePolicy1.setHeightForWidth(self.button_auto_lut.sizePolicy().hasHeightForWidth())
        self.button_auto_lut.setSizePolicy(sizePolicy1)

        self.hlayout_lut_set.addWidget(self.button_auto_lut)


        self.vlayout_panel.addLayout(self.hlayout_lut_set)

        self.spacer_panel = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.vlayout_panel.addItem(self.spacer_panel)


        self.hlayout_all.addLayout(self.vlayout_panel)


        self.gridLayout.addLayout(self.hlayout_all, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 30))
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy4)
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_file.setGeometry(QRect(366, 164, 300, 233))
        sizePolicy4.setHeightForWidth(self.menu_file.sizePolicy().hasHeightForWidth())
        self.menu_file.setSizePolicy(sizePolicy4)
        self.menu_file.setMinimumSize(QSize(300, 0))
        self.menu_file.setAcceptDrops(True)
        self.menu_view = QMenu(self.menubar)
        self.menu_view.setObjectName(u"menu_view")
        sizePolicy4.setHeightForWidth(self.menu_view.sizePolicy().hasHeightForWidth())
        self.menu_view.setSizePolicy(sizePolicy4)
        self.menu_view.setMinimumSize(QSize(300, 0))
        self.menu_view.setAcceptDrops(True)
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        sizePolicy4.setHeightForWidth(self.menu_help.sizePolicy().hasHeightForWidth())
        self.menu_help.setSizePolicy(sizePolicy4)
        self.menu_help.setMinimumSize(QSize(300, 0))
        self.menu_help.setAcceptDrops(True)
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_view.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_open_image)
        self.menu_file.addAction(self.action_load_spots)
        self.menu_file.addAction(self.action_save_spots)
        self.menu_file.addAction(self.action_save_spots_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.menu_view.addAction(self.action_zoom_in)
        self.menu_view.addAction(self.action_zoom_out)
        self.menu_view.addAction(self.action_reset_zoom)
        self.menu_help.addAction(self.action_quick_help)
        self.menu_help.addAction(self.action_about)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_open_image.setText(QCoreApplication.translate("MainWindow", u"&Open Image", None))
        self.action_load_spots.setText(QCoreApplication.translate("MainWindow", u"&Load Spots", None))
        self.action_save_spots.setText(QCoreApplication.translate("MainWindow", u"&Save Spots", None))
        self.action_save_spots_as.setText(QCoreApplication.translate("MainWindow", u"Save Spots &As", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"&Exit", None))
        self.action_zoom_in.setText(QCoreApplication.translate("MainWindow", u"Zoom &In", None))
        self.action_zoom_out.setText(QCoreApplication.translate("MainWindow", u"Zoom &Out", None))
        self.action_reset_zoom.setText(QCoreApplication.translate("MainWindow", u"&Reset Zoom", None))
        self.action_quick_help.setText(QCoreApplication.translate("MainWindow", u"&Quick Help", None))
        self.action_about.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.label_zstack.setText(QCoreApplication.translate("MainWindow", u"Z:", None))
        self.label_time.setText(QCoreApplication.translate("MainWindow", u"T:", None))
        self.label_status.setText(QCoreApplication.translate("MainWindow", u"Ready.", None))
        self.button_play.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.label_fps.setText(QCoreApplication.translate("MainWindow", u"fps", None))
        self.label_channel.setText(QCoreApplication.translate("MainWindow", u"Channel and LUT:", None))
        self.check_hide_others.setText(QCoreApplication.translate("MainWindow", u"Hide Others", None))
        self.check_invert_lut.setText(QCoreApplication.translate("MainWindow", u"Invert LUT", None))
        self.label_lut_lower.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_lut_upper.setText(QCoreApplication.translate("MainWindow", u"65535", None))
        self.label_upper.setText(QCoreApplication.translate("MainWindow", u"Upper Limit:", None))
        self.label_lower.setText(QCoreApplication.translate("MainWindow", u"Lower Limit:", None))
        self.button_reset_lut.setText(QCoreApplication.translate("MainWindow", u"Reset LUT", None))
        self.button_auto_lut.setText(QCoreApplication.translate("MainWindow", u"Auto LUT", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_view.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi


#!/usr/bin/env python

import numpy as np
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QCheckBox, QLabel, QGraphicsEllipseItem, QMenu
from PySide6.QtGui import QPen, QAction
from plugin.base import PluginBase

plugin_name = 'Particle Tracking'
class_name = 'SPT'
priority = 10
record_suffix = '_track.json'

class SPT (PluginBase):
    def __init__ (self):
        super().__init__()
        self.spot_list = []
        self.spot_radius = 4
        self.selected_radius = self.spot_radius * 2
        self.ghost_radius = self.spot_radius // 2
        self.spot_penwidth = 1
        self.current_spot = None
        self.adding_spot = False
        self.color_first = Qt.magenta
        self.color_cont = Qt.darkGreen
        self.color_last = Qt.blue
        self.color_ghost = Qt.darkGreen

    def init_widgets (self, vlayout):
        self.vlayout = vlayout
        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.text_message = QLabel()
        self.vlayout.addWidget(self.check_hide_tracks)
        self.vlayout.addWidget(self.text_message)
        self.update_status()
        self.update_mouse_cursor()
        self.init_context_menu()

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_onoff_tracks)

    def init_context_menu (self):
        self.context_menu = QMenu()

        action = QAction("Remove spot", self.context_menu)
        action.triggered.connect(self.slot_remove_spot)
        self.context_menu.addAction(action)

        action = QAction("Remove tree", self.context_menu)
        action.triggered.connect(self.slot_remove_tree)
        self.context_menu.addAction(action)

        action = QAction("Remove track", self.context_menu)
        action.triggered.connect(self.slot_remove_track)
        self.context_menu.addAction(action)

    def slot_onoff_tracks (self):
        if self.check_hide_tracks.isChecked():
            self.current_spot = None
            self.adding_spot = False
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def slot_remove_spot (self):
        pass

    def slot_remove_tree (self):
        pass

    def slot_remove_track (self):
        pass

    def list_scene_items (self, tcz_index):
        if self.check_hide_tracks.isChecked():
            return []

        scene_items = []
        drawn_spots = [spot for spot in self.spot_list \
                       if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                          (spot['z'] == tcz_index[2])]
        for spot in drawn_spots:
            item = QGraphicsEllipseItem(spot['x'] - self.spot_radius, spot['y'] - self.spot_radius, \
                                        self.spot_radius * 2, self.spot_radius * 2)
            item.setPen(self.select_pen(spot))
            scene_items.append(item)

        ghost_spots = [spot for spot in self.spot_list \
                       if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                          (spot['z'] == tcz_index[2] - 1 or spot['z'] == tcz_index[2] + 1)]
        for spot in ghost_spots:
            item = QGraphicsEllipseItem(spot['x'] - self.ghost_radius, spot['y'] - self.ghost_radius, \
                                        self.ghost_radius * 2, self.ghost_radius * 2)
            pen = QPen(self.color_ghost)
            pen.setWidth(self.spot_penwidth)
            item.setPen(pen)
            scene_items.append(item)

        if self.current_spot is not None:
            spot = self.current_spot
            if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and (spot['z'] == tcz_index[2]):
                item = QGraphicsEllipseItem(spot['x'] - self.selected_radius, spot['y'] - self.selected_radius, \
                                            self.selected_radius * 2, self.selected_radius * 2)
                item.setPen(self.select_pen(spot))
                scene_items.append(item)

        return scene_items

    def select_pen(self, spot):
        if spot['parent'] is None:
            pen = QPen(self.color_first)
        elif len([x for x in self.spot_list if (x['parent'] == spot['index'])]) > 0:
            pen = QPen(self.color_cont)
        else:
            pen = QPen(self.color_last)
        pen.setWidth(self.spot_penwidth)
        return pen

    def key_pressed (self, event, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return

        if event.key() == Qt.Key_Control:
            self.adding_spot = True
        elif event.key() == Qt.Key_Escape:
            self.current_spot = None
            self.adding_spot = False
            self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def key_released (self, event, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return

        if event.key() == Qt.Key_Control:
            self.adding_spot = False

        self.update_status()
        self.update_mouse_cursor()

    def mouse_clicked (self, event, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            self.current_spot = None
            self.update_status()
            self.update_mouse_cursor()
            return

        if event.button() == Qt.RightButton:
            if event.modifiers() == Qt.NoModifier:
                #if self.current_spot is not None:
                self.context_menu.exec(event.screenPos())
        elif event.button() == Qt.LeftButton:
            pos = event.scenePos()
            if event.modifiers() == Qt.CTRL:
                self.add_spot(pos.x(), pos.y(), *tcz_index, parent = None)
            elif event.modifiers() == Qt.NoModifier:
                if self.current_spot is None:
                    self.select_spot(pos.x(), pos.y(), *tcz_index)
                else:
                    spot = self.find_spot(pos.x(), pos.y(), *tcz_index)
                    if spot is not None and spot['index'] == self.current_spot['index']:
                        self.current_spot = spot
                    else:
                        self.add_spot(pos.x(), pos.y(), *tcz_index, parent = self.current_spot)

        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def mouse_moved (self, event, stack, tcz_index):
        if self.current_spot is None:
            return

        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            self.current_spot['x'] = event.scenePos().x()
            self.current_spot['y'] = event.scenePos().y()
            self.signal_update_scene.emit()

    def add_spot (self, x, y, time, channel, z_index, parent = None):
        if parent is None:
            parent_index = None
        else:
            parent_index = parent['index']
        spot = {'index': len(self.spot_list), 'time': time, 'channel': channel, \
                'x': x, 'y': y, 'z': z_index, 'parent': parent_index}
        self.spot_list.append(spot)
        self.current_spot = spot

    def delete_spot (self, index):
        pass

    def find_spot (self, x, y, time, channel, z_index):
        if len(self.spot_list) == 0:
            return None

        cand_spots = [spot for spot in self.spot_list \
                      if (x - self.spot_radius <= spot['x']) and (spot['x'] <= x + self.spot_radius) and
                         (y - self.spot_radius <= spot['y']) and (spot['y'] <= y + self.spot_radius) and
                         (spot['z'] == z_index) and (spot['time'] == time) and (spot['channel'] == channel)]

        cand_spots = sorted(cand_spots, key = lambda x: x['index'])
        if len(cand_spots) == 0:
            return None
        else:
            return cand_spots[-1]

    def select_spot (self, x, y, time, channel, z_index):
        self.current_spot = self.find_spot(x, y, time, channel, z_index)

    def update_status (self):
        if self.check_hide_tracks.isChecked():
            self.text_message.setText("Spots not shown.")
        elif self.current_spot is None:
            self.text_message.setText("Ctrl + click to start tracking.")
        else:
            self.text_message.setText("Spot = {0}. Click or hit ESC.".format(self.current_spot['index']))

    def update_mouse_cursor(self):
        if self.adding_spot or self.current_spot is not None:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)
        else:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

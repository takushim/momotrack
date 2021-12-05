#!/usr/bin/env python

import time, json
from numpyencoder import NumpyEncoder
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QMenu
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtGui import QPen, QAction
from plugin.base import PluginBase

plugin_name = 'Particle Tracking'
class_name = 'SPT'
priority = 10

class SPT (PluginBase):
    def __init__ (self):
        super().__init__()
        self.spot_list = []
        self.spot_radius = 4
        self.selected_radius = self.spot_radius * 2
        self.ghost_radius = self.spot_radius // 2
        self.spot_penwidth = 1
        self.marker_size = 4
        self.current_spot = None
        self.adding_spot = False
        self.color_first = Qt.magenta
        self.color_cont = Qt.darkGreen
        self.color_last = Qt.blue
        self.z_limits = [0, 0]
        self.t_limits = [0, 0]
        self.c_limits = [0, 0]
        self.records_modified = False
        self.record_suffix = '_track.json'

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

        action = QAction("Increment Z index", self.context_menu)
        action.triggered.connect(self.slot_z_increment)
        self.context_menu.addAction(action)

        action = QAction("Decrement Z index", self.context_menu)
        action.triggered.connect(self.slot_z_decrement)
        self.context_menu.addAction(action)

        self.context_menu.addSeparator()

        action = QAction("Remove this spot", self.context_menu)
        action.triggered.connect(self.slot_remove_spot)
        self.context_menu.addAction(action)

        action = QAction("Remove this tree", self.context_menu)
        action.triggered.connect(self.slot_remove_tree)
        self.context_menu.addAction(action)

        action = QAction("Remove from the root", self.context_menu)
        action.triggered.connect(self.slot_remove_track)
        self.context_menu.addAction(action)

    def load_records (self, records_filename):
        with open(records_filename, 'r') as f:
            json_dict = json.load(f)

        self.spot_list = json_dict['spot_list']
        self.current_spot = None
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()
        self.records_modified = False

    def save_records (self, records_filename, image_filename):
        output_dict = {'summary': {'plugin': plugin_name, \
                                   'time_stamp': time.strftime("%a %d %b %H:%M:%S %Z %Y"), \
                                   'image_filename': image_filename}, \
                       'spot_list': self.spot_list}

        with open(records_filename, 'w') as f:
            json.dump(output_dict, f, ensure_ascii = False, indent = 4, sort_keys = False, \
                      separators = (',', ': '), cls = NumpyEncoder)

        self.records_modified = False

    def clear_records (self):
        self.spot_list = []
        self.current_spot = None
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()
        self.records_modified = False

    def slot_onoff_tracks (self):
        if self.check_hide_tracks.isChecked():
            self.current_spot = None
            self.adding_spot = False
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def slot_z_increment (self):
        if self.current_spot is not None:
            self.current_spot['z'] = min(self.current_spot['z'] + 1, self.z_limits[1])
            self.signal_update_scene.emit()

    def slot_z_decrement (self):
        if self.current_spot is not None:
            self.current_spot['z'] = max(self.current_spot['z'] - 1, self.z_limits[0])
            self.signal_update_scene.emit()

    def slot_remove_spot (self):
        if self.current_spot is not None:
            self.remove_spot(self.current_spot['index'])
            self.current_spot = None
            self.signal_update_scene.emit()

    def slot_remove_tree (self):
        if self.current_spot is not None:
            self.remove_tree(self.current_spot['index'])
            self.current_spot = None
            self.signal_update_scene.emit()

    def slot_remove_track (self):
        if self.current_spot is not None:
            root_spot = self.find_root(self.current_spot['index'])
            self.remove_tree(root_spot['index'])
            self.current_spot = None
            self.signal_update_scene.emit()

    def list_scene_items (self, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return []

        scene_items = []
        if self.current_spot is not None:
            drawn_spots = [spot for spot in self.spot_list \
                        if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                            (spot['z'] == tcz_index[2]) and (spot['index'] != self.current_spot['index'])]
        else:
            drawn_spots = [spot for spot in self.spot_list \
                        if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                            (spot['z'] == tcz_index[2])]
        for spot in drawn_spots:
            scene_items.append(self.create_spot_item(spot, self.spot_radius, color = None))
            scene_items.extend(self.create_marker_items(spot, self.spot_radius, color = None))

        ghost_spots = [spot for spot in self.spot_list \
                       if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                          (spot['z'] == tcz_index[2] - 1 or spot['z'] == tcz_index[2] + 1)]
        for spot in ghost_spots:
            scene_items.append(self.create_spot_item(spot, self.ghost_radius, color = None))
            scene_items.extend(self.create_marker_items(spot, self.ghost_radius, color = None))

        if self.current_spot is not None:
            spot = self.current_spot
            if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and (spot['z'] == tcz_index[2]):
                scene_items.append(self.create_spot_item(spot, self.spot_radius, color = None))
                scene_items.append(self.create_spot_item(spot, self.selected_radius, color = None))
                scene_items.extend(self.create_marker_items(spot, self.selected_radius, color = None))

        return scene_items

    def create_spot_item (self, spot, radius, color = None):
        if color is None:
            pen = self.select_pen(spot)
        else:
            pen = QPen(color)
        pen.setWidth(self.spot_penwidth)
        item = QGraphicsEllipseItem(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2)
        item.setPen(pen)
        return item

    def create_marker_items (self, spot, radius, color = None):
        if len(self.find_children(spot)) <= 1:
            return []

        if color is None:
            pen = self.select_pen(spot)
        else:
            pen = QPen(color)
        pen.setWidth(self.spot_penwidth)

        item_list = []
        center_x = spot['x'] - radius
        center_y = spot['y'] - radius
        item = QGraphicsLineItem(center_x - self.marker_size, center_y, center_x + self.marker_size, center_y)
        item.setPen(pen)
        item_list.append(item)

        item = QGraphicsLineItem(center_x, center_y - self.marker_size, center_x, center_y + self.marker_size)
        item.setPen(pen)
        item_list.append(item)

        return item_list

    def select_pen (self, spot):
        if spot['parent'] is None:
            pen = QPen(self.color_first)
        elif len(self.find_children(spot)) > 0:
            pen = QPen(self.color_cont)
        else:
            pen = QPen(self.color_last)
        return pen

    def key_pressed (self, event, stack, tcz_index):
        self.update_limits(stack)

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
        self.update_limits(stack)

        if self.check_hide_tracks.isChecked():
            return

        if event.key() == Qt.Key_Control:
            self.adding_spot = False

        self.update_status()
        self.update_mouse_cursor()

    def mouse_clicked (self, event, stack, tcz_index):
        self.update_limits(stack)

        if self.check_hide_tracks.isChecked():
            self.current_spot = None
            self.update_status()
            self.update_mouse_cursor()
            return

        pos = event.scenePos()
        if event.button() == Qt.RightButton:
            self.select_spot(pos.x(), pos.y(), *tcz_index)
            if self.current_spot is not None:
                self.signal_update_scene.emit()
                self.context_menu.exec(event.screenPos())
        elif event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.CTRL:
                self.add_spot(pos.x(), pos.y(), *tcz_index, parent = None)
            else:
                if self.current_spot is None:
                    self.select_spot(pos.x(), pos.y(), *tcz_index)
                else:
                    spot_list = self.find_spots_by_position(pos.x(), pos.y(), *tcz_index)
                    if len(spot_list) > 0:
                        self.current_spot = spot_list[-1]
                    else:
                        self.add_spot(pos.x(), pos.y(), *tcz_index, parent = self.current_spot)
            self.signal_update_scene.emit()

        self.update_status()
        self.update_mouse_cursor()

    def mouse_moved (self, event, stack, tcz_index):
        self.update_limits(stack)

        if self.current_spot is None:
            return

        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            self.move_spot(self.current_spot, event.scenePos().x(), event.scenePos().y())
            self.signal_update_scene.emit()

    def move_spot (self, spot, x, y):
        spot['x'] = x
        spot['y'] = y
        self.records_modified = True

    def add_spot (self, x, y, time, channel, z_index, parent = None):
        if parent is None:
            parent_index = None
        else:
            parent_index = parent['index']
        spot = {'index': len(self.spot_list), 'time': time, 'channel': channel, \
                'x': x, 'y': y, 'z': z_index, 'parent': parent_index}
        print("Adding spot", spot)
        self.spot_list.append(spot)
        self.current_spot = spot
        self.records_modified = True

    def remove_tree (self, index):
        delete_spot = self.find_spot(index)
        child_list = self.find_children(delete_spot)

        for child_spot in child_list:
            self.remove_tree(child_spot['index'])

        self.remove_spot(delete_spot['index'])
        self.records_modified = True

    def remove_spot (self, index):
        delete_spot = self.find_spot(index)
        print("Removing spot", delete_spot)
        for child_spot in self.find_children(delete_spot):
            child_spot['parent'] = None
        self.spot_list = [spot for spot in self.spot_list if spot['index'] != index]
        self.records_modified = True

    def find_root (self, index):
        current_spot = self.find_spot(index)
        parent_spot = self.find_spot(current_spot['parent'])
        while current_spot['parent'] is not None:
            current_spot = parent_spot
            parent_spot = self.find_spot(current_spot['parent'])
        return current_spot

    def find_children (self, spot):
        if spot is None:
            spot_list = []
        else:
            spot_list = [x for x in self.spot_list if (x['parent'] == spot['index'])]
        
        return spot_list

    def find_spot (self, index):
        spot_list = [spot for spot in self.spot_list if spot['index'] == index]
        if len(spot_list) > 1:
            print("Multiple spots have the same index. Using the first spot.")

        if len(spot_list) == 0:
            spot = None
        else:
            spot = spot_list[0]
        
        return spot

    def find_spots_by_position (self, x, y, time, channel, z_index):
        if len(self.spot_list) == 0:
            return []

        cand_spots = [spot for spot in self.spot_list \
                      if (x - self.spot_radius <= spot['x']) and (spot['x'] <= x + self.spot_radius) and
                         (y - self.spot_radius <= spot['y']) and (spot['y'] <= y + self.spot_radius) and
                         (spot['z'] == z_index) and (spot['time'] == time) and (spot['channel'] == channel)]

        return sorted(cand_spots, key = lambda x: x['index'])

    def select_spot (self, x, y, time, channel, z_index):
        spot_list = self.find_spots_by_position(x, y, time, channel, z_index)
        if len(spot_list) == 0:
            self.current_spot = None
        else:
            self.current_spot = spot_list[-1]

    def update_limits (self, stack):
        self.z_limits = [0, stack.z_count - 1]
        self.c_limits = [0, stack.c_count - 1]
        self.t_limits = [0, stack.t_count - 1]

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

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        return "Single-particle tracking."

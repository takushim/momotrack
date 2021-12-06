#!/usr/bin/env python

import time, json
from numpyencoder import NumpyEncoder
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QMenu, QHBoxLayout, QDoubleSpinBox
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QAction
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
        self.ghost_radius = self.spot_radius / 2
        self.spot_penwidth = 1
        self.marker_size = 1
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
        self.track_start = None

    def init_widgets (self, vlayout):
        self.vlayout = vlayout

        hlayout = QHBoxLayout()
        label = QLabel("Marker radius:")
        hlayout.addWidget(label)
        self.dspin_marker_radius = QDoubleSpinBox()
        self.dspin_marker_radius.setRange(1, 20)
        self.dspin_marker_radius.setFocusPolicy(Qt.ClickFocus)
        self.dspin_marker_radius.setSingleStep(0.1)
        self.dspin_marker_radius.setKeyboardTracking(False)
        self.dspin_marker_radius.setValue(self.spot_radius)
        hlayout.addWidget(self.dspin_marker_radius)
        self.vlayout.addLayout(hlayout)

        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.check_auto_moving = QCheckBox("Move automatically")
        self.check_auto_moving.setChecked(True)

        self.text_message = QLabel()
        self.vlayout.addWidget(self.check_hide_tracks)
        self.vlayout.addWidget(self.check_auto_moving)

        self.vlayout.addWidget(self.text_message)
        self.update_status()
        self.update_mouse_cursor()
        self.init_context_menu()

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_onoff_tracks)
        self.dspin_marker_radius.valueChanged.connect(self.slot_marker_changed)

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
        if 'marker_radius' in json_dict['summary']:
            self.update_marker_size(json_dict['summary']['marker_radius'])
        self.current_spot = None
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()
        self.records_modified = False
        self.track_start = None

    def save_records (self, records_filename, settings = {}):
        output_dict = {'summary': {'plugin': plugin_name, \
                                   'time_stamp': time.strftime("%a %d %b %H:%M:%S %Z %Y"), \
                                   'marker_radius': self.spot_radius},
                       'settings': settings, \
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

    def slot_marker_changed (self):
        self.update_marker_size(self.dspin_marker_radius.value())
        self.signal_update_scene.emit()

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
            ancestors = self.find_ancestors(self.current_spot)
            descendants = self.find_descendants(self.current_spot)
        else:
            drawn_spots = [spot for spot in self.spot_list \
                           if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                              (spot['z'] == tcz_index[2])]
            ancestors = []
            descendants = []

        for spot in drawn_spots:
            scene_items.append(self.create_spot_item(spot, self.spot_radius, color = None))
            scene_items.extend(self.create_node_marker_items(spot, self.spot_radius, color = None))
            if spot in ancestors:
                scene_items.extend(self.create_relative_marker_items(spot, self.spot_radius, color = None, fill = True))
            if spot in descendants:
                scene_items.extend(self.create_relative_marker_items(spot, self.spot_radius, color = None, fill = False))

        ghost_spots = [spot for spot in self.spot_list \
                       if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                          (spot['z'] == tcz_index[2] - 1 or spot['z'] == tcz_index[2] + 1)]
        for spot in ghost_spots:
            scene_items.append(self.create_spot_item(spot, self.ghost_radius, color = None))
            scene_items.extend(self.create_node_marker_items(spot, self.ghost_radius, color = None))
            if spot in ancestors:
                scene_items.extend(self.create_relative_marker_items(spot, self.ghost_radius, color = None, fill = True))
            if spot in descendants:
                scene_items.extend(self.create_relative_marker_items(spot, self.ghost_radius, color = None, fill = False))

        if self.current_spot is not None:
            spot = self.current_spot
            if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and (spot['z'] == tcz_index[2]):
                scene_items.append(self.create_spot_item(spot, self.spot_radius, color = None))
                scene_items.append(self.create_spot_item(spot, self.selected_radius, color = None))
                scene_items.extend(self.create_node_marker_items(spot, self.selected_radius, color = None))

        return scene_items

    def create_spot_item (self, spot, radius, color = None):
        if color is None:
            pen = QPen(self.select_color(spot))
        else:
            pen = QPen(color)
        pen.setWidth(self.spot_penwidth)
        item = QGraphicsEllipseItem(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2)
        item.setPen(pen)
        return item

    def create_relative_marker_items (self, spot, radius, color = None, fill = False):
        if color is None:
            color = self.select_color(spot)

        item = QGraphicsEllipseItem(spot['x'] - radius - self.marker_size, spot['y'] - radius - self.marker_size, \
                                    self.marker_size * 2, self.marker_size * 2)
        pen = QPen(self.select_color(spot))
        pen.setWidth(self.spot_penwidth)
        item.setPen(QPen(self.select_color(spot)))
        if fill is True:
            item.setBrush(QBrush(self.select_color(spot)))
        return [item]

    def create_node_marker_items (self, spot, radius, color = None, fill = False):
        child_count = len(self.find_children(spot))
        if child_count <= 1:
            return []

        item = QGraphicsTextItem()
        item.setPlainText(str(child_count))
        item.setPos(spot['x'] + radius, spot['y'] - radius)
        item.setDefaultTextColor(self.select_color(spot))
        item.setScale(0.5)
        return [item]

    def select_color (self, spot):
        if spot['parent'] is None:
            color = self.color_first
        elif len(self.find_children(spot)) > 0:
            color = self.color_cont
        else:
            color = self.color_last
        return color

    def key_pressed (self, event, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return

        if event.key() == Qt.Key_Control:
            self.adding_spot = True
        elif event.key() == Qt.Key_Escape:
            if self.current_spot is None:
                self.signal_update_scene.emit()
            elif self.check_auto_moving.isChecked():
                self.signal_move_by_tczindex.emit(*self.track_start)

            self.current_spot = None
            self.adding_spot = False
            self.track_start = None
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

        pos = event.scenePos()
        if event.button() == Qt.RightButton:
            self.select_spot(pos.x(), pos.y(), *tcz_index)
            if self.current_spot is not None:
                self.signal_update_scene.emit()
                self.context_menu.exec(event.screenPos())
        elif event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.CTRL:
                self.add_spot(pos.x(), pos.y(), *tcz_index, parent = None)
                self.track_start = tcz_index
                if self.check_auto_moving.isChecked():
                    self.move_time_forward(*tcz_index)
            elif event.modifiers() == Qt.SHIFT:
                if self.current_spot is not None:
                    self.move_spot(self.current_spot, pos.x(), pos.y(), *tcz_index)
            else:
                spot_list = self.find_spots_by_position(pos.x(), pos.y(), *tcz_index)
                if len(spot_list) > 0:
                    self.current_spot = spot_list[-1]
                    self.track_start = tcz_index
                else:
                    self.add_spot(pos.x(), pos.y(), *tcz_index, parent = self.current_spot)
                    if self.check_auto_moving.isChecked():
                        self.move_time_forward(*tcz_index)
                
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def mouse_moved (self, event, stack, tcz_index):
        if self.current_spot is None:
            return
        
        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            self.move_spot(self.current_spot, event.scenePos().x(), event.scenePos().y(), *tcz_index)
            self.signal_update_scene.emit()

    def move_spot (self, spot, x, y, time, channel, z_index):
        spot['x'] = x
        spot['y'] = y
        spot['z'] = z_index
        spot['time'] = time
        spot['channel'] = channel
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

    def find_ancestors(self, spot):
        spot_list = []
        current_spot = self.find_spot(spot['parent'])
        while current_spot is not None:
            spot_list.append(current_spot)
            current_spot = self.find_spot(current_spot['parent'])
        return spot_list

    def find_descendants(self, spot):
        spot_list = []
        child_list = self.find_children(spot)
        for child in child_list:
            spot_list.append(child)
            spot_list.extend(self.find_descendants(child))
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

    def move_time_forward(self, time, channel, z_index):
        time = min(time + 1, self.t_limits[1])
        self.signal_move_by_tczindex.emit(time, channel, z_index)

    def update_stack_info (self, stack):
        self.z_limits = [0, stack.z_count - 1]
        self.c_limits = [0, stack.c_count - 1]
        self.t_limits = [0, stack.t_count - 1]

    def update_status (self):
        if self.check_hide_tracks.isChecked():
            self.text_message.setText("Spots not shown.")
        elif self.current_spot is None:
            self.text_message.setText("No spots selected\n" +
                                      "* Ctrl + click to start tracking.\n" +
                                      "* Click to select.")
        else:
            self.text_message.setText("Spot {0} selected.\n".format(self.current_spot['index']) +
                                      "* Click to add track.\n" +
                                      "* Shift + click: move.\n" +
                                      "* ESC to quit.")

    def update_marker_size (self, radius):
        self.spot_radius = radius
        self.ghost_radius = self.spot_radius / 2
        self.selected_radius = self.spot_radius * 2

    def update_mouse_cursor(self):
        if self.adding_spot or self.current_spot is not None:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)
        else:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        return "Single-particle tracking."

#!/usr/bin/env python

import time, json
from numpyencoder import NumpyEncoder
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QMenu
from PySide6.QtWidgets import QHBoxLayout, QDoubleSpinBox, QSpinBox
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem
from PySide6.QtGui import QPen, QBrush, QAction, QPainterPath
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
        self.ghost_z_range = 1
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

        self.check_auto_moving = QCheckBox("Move automatically")
        self.check_auto_moving.setChecked(True)
        self.vlayout.addWidget(self.check_auto_moving)

        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.vlayout.addWidget(self.check_hide_tracks)

        hlayout = QHBoxLayout()
        label = QLabel("Marker radius:")
        hlayout.addWidget(label)
        self.dspin_marker_radius = QDoubleSpinBox()
        self.dspin_marker_radius.setRange(1, 40)
        self.dspin_marker_radius.setFocusPolicy(Qt.ClickFocus)
        self.dspin_marker_radius.setSingleStep(0.1)
        self.dspin_marker_radius.setKeyboardTracking(False)
        self.dspin_marker_radius.setValue(self.spot_radius)
        hlayout.addWidget(self.dspin_marker_radius)
        self.vlayout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        label = QLabel("Marker line width:")
        hlayout.addWidget(label)
        self.dspin_marker_penwidth = QDoubleSpinBox()
        self.dspin_marker_penwidth.setRange(0.1, 10)
        self.dspin_marker_penwidth.setFocusPolicy(Qt.ClickFocus)
        self.dspin_marker_penwidth.setSingleStep(0.1)
        self.dspin_marker_penwidth.setKeyboardTracking(False)
        self.dspin_marker_penwidth.setValue(self.spot_penwidth)
        hlayout.addWidget(self.dspin_marker_penwidth)
        self.vlayout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        label = QLabel("Ghost z-range:")
        hlayout.addWidget(label)
        self.spin_ghost_z_range = QSpinBox()
        self.spin_ghost_z_range.setRange(1, 100)
        self.spin_ghost_z_range.setFocusPolicy(Qt.ClickFocus)
        self.spin_ghost_z_range.setSingleStep(1)
        self.spin_ghost_z_range.setKeyboardTracking(False)
        self.spin_ghost_z_range.setValue(self.ghost_z_range)
        hlayout.addWidget(self.spin_ghost_z_range)
        self.vlayout.addLayout(hlayout)

        self.text_message = QLabel()
        self.vlayout.addWidget(self.text_message)

        self.update_status()
        self.update_mouse_cursor()
        self.init_context_menu()

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_onoff_tracks)
        self.dspin_marker_radius.valueChanged.connect(self.slot_marker_changed)
        self.spin_ghost_z_range.valueChanged.connect(self.slot_marker_changed)
        self.dspin_marker_penwidth.valueChanged.connect(self.slot_marker_changed)

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
            self.dspin_marker_radius.setValue(json_dict['summary']['marker_radius'])

        if 'marker_penwidth' in json_dict['summary']:
            self.dspin_marker_penwidth.setValue(json_dict['summary']['marker_penwidth'])

        if 'ghost_z_range' in json_dict['summary']:
            self.spin_ghost_z_range.setValue(json_dict['summary']['ghost_z_range'])

        self.current_spot = None
        self.records_modified = False
        self.track_start = None

        self.update_status()
        self.update_mouse_cursor()
        self.signal_update_scene.emit()

    def save_records (self, records_filename, settings = {}):
        output_dict = {'summary': {'plugin': plugin_name, \
                                   'time_stamp': time.strftime("%a %d %b %H:%M:%S %Z %Y"), \
                                   'marker_radius': self.spot_radius,
                                   'marker_penwidth': self.spot_penwidth,
                                   'ghost_z_range': self.ghost_z_range},
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
        self.ghost_z_range = self.spin_ghost_z_range.value()
        self.spot_penwidth = self.dspin_marker_penwidth.value()
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
        candidate_spots = [spot for spot in self.spot_list \
                           if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and (spot != self.current_spot)]

        if self.current_spot is not None:
            scene_items.extend(self.list_spot_items([self.current_spot], self.spot_radius))
            scene_items.extend(self.list_spot_items([self.current_spot], self.selected_radius))
            scene_items.extend(self.list_node_items([self.current_spot], self.selected_radius))
            ancestors = self.find_ancestors(self.current_spot)
            descendants = self.find_descendants(self.current_spot)
        else:
            ancestors = []
            descendants = []

        existing_spots = [spot for spot in candidate_spots if (spot['z'] == tcz_index[2])]
        scene_items.extend(self.list_spot_items(existing_spots, self.spot_radius))
        scene_items.extend(self.list_node_items(existing_spots, self.spot_radius))

        ghost_spots = [spot for spot in candidate_spots \
                       if (abs(spot['z'] - tcz_index[2]) <= self.ghost_z_range) and (spot['z'] != tcz_index[2])]
        scene_items.extend(self.list_spot_items(ghost_spots, self.ghost_radius))
        scene_items.extend(self.list_node_items(ghost_spots, self.ghost_radius))

        for spot in existing_spots:
            if spot in ancestors:
                scene_items.extend(self.create_relative_marker_items(spot, self.spot_radius, color = None, fill = True))
            if spot in descendants:
                scene_items.extend(self.create_relative_marker_items(spot, self.spot_radius, color = None, fill = False))

        for spot in ghost_spots:
            if spot in ancestors:
                scene_items.extend(self.create_relative_marker_items(spot, self.ghost_radius, color = None, fill = True))
            if spot in descendants:
                scene_items.extend(self.create_relative_marker_items(spot, self.ghost_radius, color = None, fill = False))

        return scene_items

    def list_spot_items (self, spot_list, radius):
        spots_first = [spot for spot in spot_list if spot['parent'] is None]
        spots_last = [spot for spot in spot_list if (len(self.find_children(spot)) == 0) and (spot not in spots_first)]
        spots_cont = [spot for spot in spot_list if (spot not in spots_first) and (spot not in spots_last)]

        items_first = [self.create_spot_item(spot, radius, QPen(self.color_first)) for spot in spots_first]
        items_last = [self.create_spot_item(spot, radius, QPen(self.color_last)) for spot in spots_last]
        items_cont = [self.create_spot_item(spot, radius, QPen(self.color_cont)) for spot in spots_cont]

        spots_one = [spot for spot in spot_list if (spot['parent'] is None) and (len(self.find_children(spot)) == 0)]
        items_one = [self.create_spot_item_one(spot, radius, QPen(self.color_last)) for spot in spots_one]

        return items_first + items_last + items_cont + items_one

    def create_spot_item (self, spot, radius, pen):
        item = QGraphicsEllipseItem(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2)
        item.setPen(pen)
        return item

    def create_spot_item_one (self, spot, radius, pen):
        path = QPainterPath()
        path.arcMoveTo(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2, 225.0)
        path.arcTo(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2, 225.0, 180)

        item = QGraphicsPathItem(path)
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

    def list_node_items (self, spot_list, radius):
        spot_list = [spot for spot in spot_list if len(self.find_children(spot)) > 1]

        spots_first = [spot for spot in spot_list if spot['parent'] is None]
        spots_last = [spot for spot in spot_list if (len(self.find_children(spot)) == 0) and (spot not in spots_first)]
        spots_cont = [spot for spot in spot_list if (spot not in spots_first) and (spot not in spots_last)]

        items_first = [self.create_node_item(spot, radius, self.color_first) for spot in spots_first]
        items_last = [self.create_node_item(spot, radius, self.color_last) for spot in spots_last]
        items_cont = [self.create_node_item(spot, radius, self.color_cont) for spot in spots_cont]

        return items_first + items_last + items_cont

    def create_node_item (self, spot, radius, color):
        child_count = len(self.find_children(spot))

        item = QGraphicsTextItem()
        item.setPlainText(str(child_count))
        item.setPos(spot['x'] + radius, spot['y'] - radius)
        item.setDefaultTextColor(color)
        item.setScale(0.5)

        return item

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
            if self.check_auto_moving.isChecked():
                self.signal_move_by_tczindex.emit(*self.track_start)

            self.current_spot = None
            self.adding_spot = False
            self.track_start = None
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

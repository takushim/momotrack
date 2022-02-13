#!/usr/bin/env python

import textwrap
from datetime import datetime
from logging import getLogger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QMenu
from PySide6.QtWidgets import QHBoxLayout, QDoubleSpinBox, QSpinBox, QLineEdit
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem
from PySide6.QtGui import QColor, QPen, QBrush, QAction, QPainterPath, QFont, QTextDocument
from plugin.base import PluginBase, PluginException

logger = getLogger(__name__)

plugin_name = 'Particle Tracking'
class_name = 'SPT'
priority = 10

class SPT (PluginBase):
    def __init__ (self):
        super().__init__()
        self.plugin_name = str(plugin_name)
        self.spot_list = []
        self.current_spot = None
        self.adding_spot = False
        self.is_tracking = False
        self.z_limits = [0, 0]
        self.t_limits = [0, 0]
        self.c_limits = [0, 0]
        self.records_modified = False
        self.record_suffix = '_track.json'
        self.records_dict = {}
        self.track_start = None
        self.image_settings = {}
        self.update_settings()

    def init_widgets (self, vlayout):
        self.vlayout = vlayout

        self.check_auto_moving = QCheckBox("Move automatically")
        self.vlayout.addWidget(self.check_auto_moving)

        self.check_hide_tracks = QCheckBox("Hide All Tracks")
        self.vlayout.addWidget(self.check_hide_tracks)

        hlayout = QHBoxLayout()
        label = QLabel("Marker radius:")
        hlayout.addWidget(label)
        self.dspin_marker_radius = QDoubleSpinBox()
        self.dspin_marker_radius.setRange(1, 40)
        self.dspin_marker_radius.setFocusPolicy(Qt.ClickFocus)
        self.dspin_marker_radius.setKeyboardTracking(False)
        self.dspin_marker_radius.setSingleStep(0.1)
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
        self.text_message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.vlayout.addWidget(self.text_message)

        self.load_settings()
        self.update_status()
        self.update_mouse_cursor()
        self.init_context_menu()

    def connect_signals (self):
        self.check_hide_tracks.stateChanged.connect(self.slot_onoff_tracks)
        self.dspin_marker_radius.valueChanged.connect(self.slot_marker_radius_changed)
        self.dspin_marker_radius.editingFinished.connect(self.slot_return_focus)
        self.dspin_marker_penwidth.valueChanged.connect(self.slot_marker_penwidth_changed)
        self.dspin_marker_penwidth.editingFinished.connect(self.slot_return_focus)
        self.spin_ghost_z_range.valueChanged.connect(self.slot_ghost_z_range_changed)
        self.spin_ghost_z_range.editingFinished.connect(self.slot_return_focus)

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
        try:
            super().load_records(records_filename)

            self.spot_list = self.records_dict.get('spot_list', [])
            self.load_settings(self.records_dict.get('plugin_settings', {}))

            for spot in self.spot_list:
                self.update_old_spot(spot)

            self.clear_tracking()
            self.records_modified = False

            self.update_status()
            self.update_mouse_cursor()
            self.signal_update_scene.emit()

        except PluginException:
            raise

    def save_records (self, records_filename, settings = {}):
        self.records_dict = {'plugin_settings': self.archive_settings(),
                             'spot_list': self.spot_list}
        super().save_records(records_filename, settings)
        self.records_modified = False

    def load_settings (self, settings = {}):
        self.update_settings(settings)
        self.dspin_marker_radius.setValue(self.spot_radius)
        self.dspin_marker_penwidth.setValue(self.spot_penwidth)
        self.spin_ghost_z_range.setValue(self.ghost_z_range)
        self.check_auto_moving.setChecked(settings.get('move_auto', True))
        self.check_hide_tracks.setChecked(settings.get('hide_tracks', False))

    def update_settings (self, settings = {}):
        self.spot_radius = settings.get('spot_radius', 2)
        self.spot_penwidth = settings.get('spot_penwidth', 0.2)
        self.ghost_z_range = settings.get('ghost_z_range', 5)
        self.color_first = settings.get('color_first', 'magenta')
        self.color_cont = settings.get('color_cont', 'darkGreen')
        self.color_last = settings.get('color_last', 'blue')
        self.update_marker_radii(self.spot_radius)

    def archive_settings (self):
        settings = {'spot_radius': self.spot_radius,
                    'spot_penwidth': self.spot_penwidth,
                    'ghost_z_range': self.ghost_z_range,
                    'color_first': self.color_first,
                    'color_cont': self.color_cont,
                    'color_last': self.color_last,
                    'move_auto': self.check_auto_moving.isChecked(),
                    'hide_tracks': self.check_hide_tracks.isChecked()}
        return settings

    def clear_records (self):
        super().clear_records()
        self.spot_list = []
        self.clear_tracking()
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

    def slot_marker_radius_changed (self):
        self.update_marker_radii(self.dspin_marker_radius.value())
        self.dspin_marker_radius.clearFocus()
        self.signal_update_scene.emit()

    def slot_marker_penwidth_changed (self):
        self.spot_penwidth = self.dspin_marker_penwidth.value()
        self.dspin_marker_penwidth.clearFocus()
        self.signal_update_scene.emit()

    def slot_ghost_z_range_changed (self):
        self.ghost_z_range = self.spin_ghost_z_range.value()
        self.spin_ghost_z_range.clearFocus()
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
            self.clear_tracking()
            self.signal_update_scene.emit()

    def slot_remove_tree (self):
        if self.current_spot is not None:
            self.remove_tree(self.current_spot['index'])
            self.clear_tracking()
            self.signal_update_scene.emit()

    def slot_remove_track (self):
        if self.current_spot is not None:
            root_spot = self.find_root(self.current_spot['index'])
            self.remove_tree(root_spot['index'])
            self.clear_tracking()
            self.signal_update_scene.emit()

    def slot_return_focus (self):
        self.dspin_marker_penwidth.findChild(QLineEdit).deselect()
        self.dspin_marker_radius.findChild(QLineEdit).deselect()
        self.spin_ghost_z_range.findChild(QLineEdit).deselect()
        self.signal_focus_graphics_view.emit()

    def list_scene_items (self, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return []

        scene_items = []
        candidate_spots = [spot for spot in self.spot_list \
                           if (spot['time'] == tcz_index[0]) and (spot['channel'] == tcz_index[1]) and
                              (spot['delete'] == False)]

        deselected_spots = [spot for spot in candidate_spots \
                            if (spot['z'] == tcz_index[2]) and (spot != self.current_spot)]
        scene_items.extend(self.list_spot_items(deselected_spots, self.spot_radius))
        scene_items.extend(self.list_node_items(deselected_spots, self.spot_radius))

        ghost_spots = [spot for spot in candidate_spots \
                       if (abs(spot['z'] - tcz_index[2]) <= self.ghost_z_range) and \
                          (spot['z'] != tcz_index[2])]
        scene_items.extend(self.list_spot_items(ghost_spots, self.ghost_radius))
        scene_items.extend(self.list_node_items(ghost_spots, self.ghost_radius))

        if self.current_spot is not None:
            if (self.current_spot['time'] == tcz_index[0]) and \
               (self.current_spot['channel'] == tcz_index[1]):
                if self.current_spot['z'] == tcz_index[2]:
                    scene_items.extend(self.list_spot_items([self.current_spot], self.spot_radius))
                    scene_items.extend(self.list_spot_items([self.current_spot], self.selected_radius))
                    scene_items.extend(self.list_node_items([self.current_spot], self.selected_radius))
                elif abs(self.current_spot['z'] - tcz_index[2]) < self.ghost_z_range:
                    scene_items.extend(self.list_spot_items([self.current_spot], self.ghost_radius))
                    scene_items.extend(self.list_spot_items([self.current_spot], self.selected_ghost_radius))
                    scene_items.extend(self.list_node_items([self.current_spot], self.selected_ghost_radius))

            existing_ancestors = [spot for spot in self.find_ancestors(self.current_spot) if spot in deselected_spots]
            existing_descendants = [spot for spot in self.find_descendants(self.current_spot) if spot in deselected_spots]
            scene_items.extend(self.list_ancestor_items(existing_ancestors, self.spot_radius))
            scene_items.extend(self.list_descendant_items(existing_descendants, self.spot_radius))

            ghost_ancestors = [spot for spot in self.find_ancestors(self.current_spot) if spot in ghost_spots]
            ghots_descendants = [spot for spot in self.find_descendants(self.current_spot) if spot in ghost_spots]
            scene_items.extend(self.list_ancestor_items(ghost_ancestors, self.ghost_radius))
            scene_items.extend(self.list_descendant_items(ghots_descendants, self.ghost_radius))

        return scene_items

    def list_spot_items (self, spot_list, radius):
        spots_first = [spot for spot in spot_list if spot['parent'] is None]
        spots_last = [spot for spot in spot_list if (len(self.find_children(spot)) == 0) and (spot not in spots_first)]
        spots_cont = [spot for spot in spot_list if (spot not in spots_first) and (spot not in spots_last)]

        items_first = [self.create_spot_item(spot, radius, self.color_first) for spot in spots_first]
        items_last = [self.create_spot_item(spot, radius, self.color_last) for spot in spots_last]
        items_cont = [self.create_spot_item(spot, radius, self.color_cont) for spot in spots_cont]

        spots_one = [spot for spot in spot_list if (spot['parent'] is None) and (len(self.find_children(spot)) == 0)]
        items_one = [self.create_spot_item_one(spot, radius, self.color_last) for spot in spots_one]

        return items_first + items_last + items_cont + items_one

    def create_spot_item (self, spot, radius, color):
        item = QGraphicsEllipseItem(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2)

        pen = QPen(QColor(color))
        pen.setWidthF(self.spot_penwidth)
        item.setPen(pen)

        return item

    def create_spot_item_one (self, spot, radius, color):
        path = QPainterPath()
        path.arcMoveTo(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2, 225.0)
        path.arcTo(spot['x'] - radius, spot['y'] - radius, radius * 2, radius * 2, 225.0, 180)

        pen = QPen(QColor(color))
        pen.setWidthF(self.spot_penwidth)
        item = QGraphicsPathItem(path)
        item.setPen(pen)

        return item

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
        document = QTextDocument(str(len(self.find_children(spot))))
        document.setDocumentMargin(0)
        font = QFont()
        font.setPixelSize(self.spot_radius * 2)

        item = QGraphicsTextItem()
        item.setDocument(document)
        item.setDefaultTextColor(QColor(color))
        item.setFont(font)
        item.setPos(spot['x'] + radius, spot['y'] - radius - item.boundingRect().height())

        return item

    def list_ancestor_items (self, spot_list, radius):
        spots_first = [spot for spot in spot_list if spot['parent'] is None]
        spots_last = [spot for spot in spot_list if (len(self.find_children(spot)) == 0) and (spot not in spots_first)]
        spots_cont = [spot for spot in spot_list if (spot not in spots_first) and (spot not in spots_last)]

        items_first = [self.create_ancestor_item(spot, radius, self.color_first) for spot in spots_first]
        items_last = [self.create_ancestor_item(spot, radius, self.color_last) for spot in spots_last]
        items_cont = [self.create_ancestor_item(spot, radius, self.color_cont) for spot in spots_cont]

        return items_first + items_last + items_cont

    def create_ancestor_item (self, spot, radius, color):
        item = QGraphicsEllipseItem(spot['x'] - radius - self.marker_radius, spot['y'] - radius - self.marker_radius, \
                                    self.marker_radius * 2, self.marker_radius * 2)

        pen = QPen(QColor(color))
        pen.setWidthF(self.spot_penwidth)
        item.setPen(pen)

        if (self.current_spot is not None) and (spot['index'] == self.current_spot['parent']):
            item.setBrush(QBrush(QColor(color)))

        return item

    def list_descendant_items (self, spot_list, radius):
        spots_first = [spot for spot in spot_list if spot['parent'] is None]
        spots_last = [spot for spot in spot_list if (len(self.find_children(spot)) == 0) and (spot not in spots_first)]
        spots_cont = [spot for spot in spot_list if (spot not in spots_first) and (spot not in spots_last)]

        items_first = [self.create_descendant_item(spot, radius, self.color_first) for spot in spots_first]
        items_last = [self.create_descendant_item(spot, radius, self.color_last) for spot in spots_last]
        items_cont = [self.create_descendant_item(spot, radius, self.color_cont) for spot in spots_cont]

        return items_first + items_last + items_cont

    def create_descendant_item (self, spot, radius, color):
        item = QGraphicsEllipseItem(spot['x'] + radius - self.marker_radius, \
                                    spot['y'] + radius - self.marker_radius, \
                                    self.marker_radius * 2, self.marker_radius * 2)

        pen = QPen(QColor(color))
        pen.setWidthF(self.spot_penwidth)
        item.setPen(pen)

        if (self.current_spot is not None) and (spot['parent'] == self.current_spot['index']):
            item.setBrush(QBrush(QColor(color)))

        return item

    def key_pressed (self, event, stack, tcz_index):
        if self.check_hide_tracks.isChecked():
            return

        if event.key() == Qt.Key_Control:
            self.adding_spot = True
        elif event.key() == Qt.Key_Escape:
            if self.is_tracking and self.check_auto_moving.isChecked():
                self.signal_move_by_tczindex.emit(*self.track_start)
            self.clear_tracking()
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

    def mouse_pressed (self, event, stack, tcz_index):
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
            else:
                self.clear_tracking()
        elif event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.CTRL:
                self.add_spot(pos.x(), pos.y(), *tcz_index, parent = None)
                self.is_tracking = True
                self.track_start = tcz_index
                self.last_tczindex = tcz_index
            elif event.modifiers() == Qt.SHIFT:
                if self.current_spot is not None:
                    self.move_spot(self.current_spot, pos.x(), pos.y(), *tcz_index)
                else:
                    self.clear_tracking()
            else:
                spot_list = self.find_spots_by_position(pos.x(), pos.y(), *tcz_index)
                if len(spot_list) > 0:
                    self.clear_tracking()
                    self.current_spot = spot_list[-1]
                    self.track_start = tcz_index
                elif self.current_spot is not None:
                    self.add_spot(pos.x(), pos.y(), *tcz_index, parent = self.current_spot)
                    self.is_tracking = True
                    self.last_tczindex = tcz_index
                
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def mouse_moved (self, event, stack, tcz_index):
        if self.current_spot is not None and event.buttons() == Qt.LeftButton:
            self.move_spot(self.current_spot, event.scenePos().x(), event.scenePos().y(), *tcz_index)
            self.signal_update_scene.emit()

    def mouse_released (self, event, stack, tcz_index):
        if event.button() == Qt.LeftButton:
            if self.check_auto_moving.isChecked():
                if self.is_tracking and self.last_tczindex is not None:
                    # avoid moving forward twice (fast click breaks the pair of press and release??)
                    self.move_time_forward(*self.last_tczindex)
                    self.last_tczindex = None
                
        self.signal_update_scene.emit()
        self.update_status()
        self.update_mouse_cursor()

    def clear_tracking (self):
        self.current_spot = None
        self.adding_spot = False
        self.is_tracking = False
        self.track_start = None
        self.last_tczindex = None

    def move_spot (self, spot, x, y, t_index, channel, z_index):
        spot['x'] = x
        spot['y'] = y
        spot['z'] = z_index
        spot['time'] = t_index
        spot['channel'] = channel
        spot['update'] = datetime.now().astimezone().isoformat()
        self.records_modified = True

    def add_spot (self, x, y, t_index, channel, z_index, parent = None):
        if parent is None:
            parent_index = None
        else:
            parent_index = parent['index']

        if len(self.spot_list) == 0:
            index = 0
        else:
            index = max([spot['index'] for spot in self.spot_list]) + 1

        spot = self.create_spot(index = index, time = t_index, channel = channel, \
                                x = x, y = y, z = z_index, parent = parent_index)

        logger.info("Adding spot: {0}".format(spot))
        self.spot_list.append(spot)
        self.current_spot = spot
        self.records_modified = True

    def create_spot (self, index = None, time = None, channel = None, x = None, y = None, z = None, parent = None):
        spot = {'index': index, 'time': time, 'channel': channel, \
                'x': x, 'y': y, 'z': z, 'parent': parent, 'label': None, \
                'delete': False, \
                'create': datetime.now().astimezone().isoformat(), \
                'update': datetime.now().astimezone().isoformat()}
        return spot

    def update_old_spot (self, spot):
        empty_spot = self.create_spot()
        keys = empty_spot.keys().remove('index')
        if 'index' not in spot:
            logger.error("Index not in the spot: {0}. This is critical.".format(spot))
        for key in keys:
            if key not in spot:
                spot[key] = empty_spot[key]

    def remove_tree (self, index):
        delete_spot = self.find_spot_by_index(index)
        child_list = self.find_children(delete_spot)

        for child_spot in child_list:
            self.remove_tree(child_spot['index'])

        self.remove_spot(delete_spot['index'])
        self.records_modified = True

    def remove_spot (self, index):
        delete_spot = self.find_spot_by_index(index)
        logger.info("Removing spot: {0}".format(delete_spot))
        for child_spot in self.find_children(delete_spot):
            child_spot['parent'] = None
            child_spot['update'] = datetime.now().astimezone().isoformat()

        delete_spot['delete'] = True
        delete_spot['update'] = datetime.now().astimezone().isoformat()
        self.records_modified = True

    def find_root (self, index):
        current_spot = self.find_spot_by_index(index)
        parent_spot = self.find_spot_by_index(current_spot['parent'])
        while current_spot['parent'] is not None:
            current_spot = parent_spot
            parent_spot = self.find_spot_by_index(current_spot['parent'])
        return current_spot

    def find_children (self, spot):
        if spot is None:
            spot_list = []
        else:
            spot_list = [x for x in self.spot_list \
                         if (x['parent'] == spot['index']) and (x['delete'] == False)]
        
        return spot_list

    def find_ancestors(self, spot):
        spot_list = []
        current_spot = self.find_spot_by_index(spot['parent'])
        while current_spot is not None:
            spot_list.append(current_spot)
            current_spot = self.find_spot_by_index(current_spot['parent'])
        return spot_list

    def find_descendants(self, spot):
        spot_list = []
        child_list = self.find_children(spot)
        for child in child_list:
            spot_list.append(child)
            spot_list.extend(self.find_descendants(child))
        return spot_list

    def find_spot_by_index (self, index):
        spot_list = [spot for spot in self.spot_list \
                     if (spot['index'] == index) and (spot['delete'] == False)]
        if len(spot_list) > 1:
            logger.error("Multiple spots have the same index. This is a bug.")

        if len(spot_list) == 0:
            spot = None
        else:
            spot = spot_list[0]
        
        return spot

    def find_spots_by_position (self, x, y, t_index, channel, z_index):
        if len(self.spot_list) == 0:
            return []

        cand_spots = [spot for spot in self.spot_list \
                      if (spot['delete'] == False) and
                         (x - self.spot_radius <= spot['x']) and (spot['x'] <= x + self.spot_radius) and
                         (y - self.spot_radius <= spot['y']) and (spot['y'] <= y + self.spot_radius) and
                         (spot['z'] == z_index) and (spot['time'] == t_index) and (spot['channel'] == channel)]

        return sorted(cand_spots, key = lambda x: x['index'])

    def select_spot (self, x, y, t_index, channel, z_index):
        spot_list = self.find_spots_by_position(x, y, t_index, channel, z_index)
        if len(spot_list) == 0:
            self.current_spot = None
        else:
            self.current_spot = spot_list[-1]

    def move_time_forward(self, t_index, channel, z_index):
        t_index = min(t_index + 1, self.t_limits[1])
        self.signal_move_by_tczindex.emit(t_index, channel, z_index)

    def update_stack_info (self, stack):
        self.z_limits = [0, stack.z_count - 1]
        self.c_limits = [0, stack.c_count - 1]
        self.t_limits = [0, stack.t_count - 1]

    def update_status (self):
        if self.check_hide_tracks.isChecked():
            self.text_message.setText("Spots not shown.")
            return

        if self.adding_spot:
            self.text_message.setText("Click to add a spot.")
            return

        if self.current_spot is None:
            self.text_message.setText("No spot selected.")
        else:
            if self.is_tracking:
                self.text_message.setText("Tracking from t = {0}".format(self.track_start[0]))
            else:
                self.text_message.setText("Spot {0} selected.".format(self.current_spot['index']))

    def update_marker_radii (self, radius):
        self.spot_radius = radius
        self.ghost_radius = self.spot_radius / 2
        self.marker_radius = self.spot_radius / 2
        self.selected_radius = self.spot_radius * 1.5
        self.selected_ghost_radius = self.ghost_radius * 1.5

    def update_mouse_cursor(self):
        if self.adding_spot or self.current_spot is not None:
            self.signal_update_mouse_cursor.emit(Qt.CrossCursor)
        else:
            self.signal_update_mouse_cursor.emit(Qt.ArrowCursor)

    def is_modified (self):
        return self.records_modified

    def help_message (self):
        message = textwrap.dedent('''
        <b>Single-particle tracking plugin</b>
        <ul>
        <li> Ctrl + click to start new tracking.</li>
        <li> Click to select an existing spot and:</li>
            <ul>
            <li> Click to proceed tracking.</li>
            <li> Drag moves the spot within the view.</li>
            <li> Shift + click can move the spot to a different view.</li>
            <li> Adjacent dots indicate ancestors and discendants.</li>
            <li> Filled dots show direct ancestors and discendants.</li>
            </ul>
        <li> Right click on a spot to show a context menu.</li>
        <li> Check "move automatically" to proceed the time when a new spot is added.</li>
        <li> A number appears when a spot has multiple children.</li>
        </ul>
        ''')
        return message

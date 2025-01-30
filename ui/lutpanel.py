#!/usr/bin/env python

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QColor
from image import lut

class LutPanel (QObject):
    signal_update_image_view = Signal()
    signal_reset_current_lut_range = Signal()

    def __init__ (self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui
        self.ui.combo_lut.addItems([item for item in lut.lut_dict])
        self.ui.combo_bits.addItems([item for item in lut.bit_dict])

    def init_widgets (self, stack):
        self.init_luts(stack)
        self.init_boxes()
        self.update_lut_panel_silently()

        self.scene_lut = QGraphicsScene()
        self.scene_lut.setBackgroundBrush(QColor('white'))
        self.ui.gview_lut.setScene(self.scene_lut)

    def init_luts (self, stack):
        self.lut_list = []

        if stack is None:
            self.lut_list.append(lut.LUT())
        elif stack.c_count == 1:
            image_lut = lut.LUT(lut_name = "Gray", pixel_values = stack.image_array[:, 0])
            self.lut_list.append(image_lut)
        else:
            for channel in range(stack.c_count):
                lut_name = lut.lut_names[channel % len(lut.lut_names)]
                image_lut = lut.LUT(lut_name = lut_name, pixel_values = stack.image_array[:, channel])
                self.lut_list.append(image_lut)

    def init_boxes (self):
        self.ui.combo_channel.blockSignals(True)
        self.ui.combo_channel.clear()
        self.ui.combo_channel.addItems(["Channel {0}".format(i) for i in range(len(self.lut_list))])
        self.ui.combo_channel.blockSignals(False)

        lut = self.lut_list[0]
        self.ui.combo_lut.setCurrentText(lut.lut_name)
        self.ui.combo_lut.setEnabled(self.ui.check_color_always.isChecked())

        self.ui.combo_bits.setCurrentText(lut.bit_mode)
        self.ui.check_lut_invert.setChecked(lut.lut_invert)
        self.ui.dspin_auto_cutoff.setValue(lut.auto_cutoff)
        self.ui.check_auto_lut.setChecked(lut.auto_lut)

    def connect_signals_to_slots (self):
        self.ui.combo_channel.currentIndexChanged.connect(self.slot_lut_panel_changed)
        self.ui.check_composite.stateChanged.connect(self.slot_lut_panel_changed)
        self.ui.check_color_always.stateChanged.connect(self.slot_lut_panel_changed)
        self.ui.check_lut_invert.stateChanged.connect(self.slot_lut_panel_changed)
        self.ui.combo_lut.currentIndexChanged.connect(self.slot_lut_panel_changed)
        self.ui.combo_bits.currentIndexChanged.connect(self.slot_lut_panel_changed)
        self.ui.check_auto_lut.stateChanged.connect(self.slot_lut_panel_changed)
        self.ui.dspin_auto_cutoff.valueChanged.connect(self.slot_lut_panel_changed)
        self.ui.dspin_auto_cutoff.editingFinished.connect(self.slot_lut_panel_changed)
        self.ui.slider_lut_lower.valueChanged.connect(self.slot_lower_slider_changed)
        self.ui.slider_lut_upper.valueChanged.connect(self.slot_upper_slider_changed)
        self.ui.button_reset_lut_range.clicked.connect(self.slot_reset_current_lut_range)

    def restore_lut_settings (self, settings_list = []):
        for index in range(min(len(self.lut_list), len(settings_list))):
            self.lut_list[index].load_settings(settings_list[index])
        self.update_lut_panel_silently()

    def set_current_channel (self, channel = 0):
        self.ui.combo_channel.setCurrentIndex(channel)
 
    def update_lut_panel_silently (self):
        # do not send signals from this function
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        lut_range = current_lut.lut_range()

        # enable/disable combo and check boxes
        if self.ui.check_composite.isChecked() or self.ui.check_color_always.isChecked():
            self.ui.combo_lut.setEnabled(True)
        else:
            self.ui.combo_lut.setEnabled(False)

        if self.ui.check_composite.isChecked():
            self.ui.check_color_always.setEnabled(False)
        else:
            self.ui.check_color_always.setEnabled(True)

        self.ui.combo_lut.blockSignals(True)
        self.ui.combo_lut.setCurrentText(current_lut.lut_name)
        self.ui.combo_lut.blockSignals(False)

        self.ui.combo_bits.blockSignals(True)
        self.ui.combo_bits.setCurrentText(current_lut.bit_mode)
        self.ui.combo_bits.blockSignals(False)

        # update lut_invert and auto_lut
        self.ui.check_lut_invert.blockSignals(True)
        self.ui.check_lut_invert.setChecked(current_lut.lut_invert)
        self.ui.check_lut_invert.blockSignals(False)

        self.ui.check_auto_lut.blockSignals(True)
        self.ui.check_auto_lut.setChecked(current_lut.auto_lut)
        self.ui.check_auto_lut.blockSignals(False)

        self.ui.dspin_auto_cutoff.blockSignals(True)
        self.ui.dspin_auto_cutoff.setValue(current_lut.auto_cutoff)
        self.ui.dspin_auto_cutoff.blockSignals(False)

        # set sliders
        self.ui.slider_lut_upper.blockSignals(True)
        self.ui.slider_lut_lower.blockSignals(True)

        self.ui.slider_lut_upper.setMinimum(lut_range[0])
        self.ui.slider_lut_upper.setMaximum(lut_range[1])
        self.ui.slider_lut_lower.setMinimum(lut_range[0])
        self.ui.slider_lut_lower.setMaximum(lut_range[1])

        self.ui.slider_lut_upper.setValue(current_lut.lut_upper)
        self.ui.slider_lut_lower.setValue(current_lut.lut_lower)

        self.ui.slider_lut_upper.blockSignals(False)
        self.ui.slider_lut_lower.blockSignals(False)

        # set labels
        if current_lut.bit_mode == "Float":
            self.ui.label_bitrange_lower.setText(f"{lut_range[0]:.2e}")
            self.ui.label_bitrange_upper.setText(f"{lut_range[1]:.2e}")
            self.ui.label_lut_lower.setText(f"Lower limit: {current_lut.lut_lower:.2e}")
            self.ui.label_lut_upper.setText(f"Upper limit: {current_lut.lut_upper:.2e}")
        else:
            self.ui.label_bitrange_lower.setText(f"{lut_range[0]:.2f}")
            self.ui.label_bitrange_upper.setText(f"{lut_range[1]:.2f}")
            self.ui.label_lut_lower.setText(f"Lower limit: {current_lut.lut_lower:.2f}")
            self.ui.label_lut_upper.setText(f"Upper limit: {current_lut.lut_upper:.2f}")

    def update_lut_range_if_auto (self, image):
        if self.ui.check_auto_lut.isChecked():
            current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
            current_lut.set_range_by_image(image, self.ui.dspin_auto_cutoff.value())

            self.ui.slider_lut_upper.blockSignals(True)
            self.ui.slider_lut_lower.blockSignals(True)

            self.ui.slider_lut_upper.setValue(current_lut.lut_upper)
            self.ui.slider_lut_lower.setValue(current_lut.lut_lower)

            self.ui.slider_lut_upper.blockSignals(False)
            self.ui.slider_lut_lower.blockSignals(False)

    def reset_current_lut_range (self, pixel_values):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.reset_lut_range(pixel_values)
        self.update_lut_panel_silently()

    def update_lut_view (self, image):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        lut_range = current_lut.lut_range()

        width = self.ui.gview_lut.width()
        height = self.ui.gview_lut.height()
        self.scene_lut.clear()
        self.scene_lut.setSceneRect(0, 0, width, height)

        hists, bins = np.histogram(image, bins = int(width), range = lut_range)
        max_hist = np.max(hists)
        for index, hist in enumerate(hists):
            x = width * (bins[index] - np.min(bins)) / np.ptp(bins)
            y_bottom = height
            y_top = height * (1 - float(hist) / max_hist)
            self.scene_lut.addLine(x, y_bottom, x, y_top, QColor('gray'))

        if np.isclose(lut_range[0], lut_range[1]) == False:
            x_lower = width * (current_lut.lut_lower - lut_range[0]) / (lut_range[1] - lut_range[0])
            x_upper = width * (current_lut.lut_upper - lut_range[0]) / (lut_range[1] - lut_range[0])
            self.scene_lut.addLine(x_upper, 0, x_upper, height, QColor('black'))
            self.scene_lut.addLine(x_lower, height, x_upper, 0)

    def update_current_lut (self):
        current_lut = self.lut_list[self.ui.combo_channel.currentIndex()]
        current_lut.lut_name = self.ui.combo_lut.currentText()
        current_lut.lut_lower = self.ui.slider_lut_lower.value()
        current_lut.lut_upper = self.ui.slider_lut_upper.value()
        current_lut.lut_invert = self.ui.check_lut_invert.isChecked()
        current_lut.bit_mode = self.ui.combo_bits.currentText()
        current_lut.auto_lut = self.ui.check_auto_lut.isChecked()
        current_lut.auto_cutoff = self.ui.dspin_auto_cutoff.value()

    def slot_upper_slider_changed (self):
        self.ui.check_auto_lut.blockSignals(True)
        self.ui.check_auto_lut.setChecked(False)
        self.ui.check_auto_lut.blockSignals(False)

        self.ui.slider_lut_upper.blockSignals(True)
        self.ui.slider_lut_upper.setValue(max(self.ui.slider_lut_upper.value(), self.ui.slider_lut_lower.value()))
        self.ui.slider_lut_upper.blockSignals(False)

        self.update_current_lut()
        self.update_lut_panel_silently()
        self.signal_update_image_view.emit()

    def slot_lower_slider_changed (self):
        self.ui.check_auto_lut.blockSignals(True)
        self.ui.check_auto_lut.setChecked(False)
        self.ui.check_auto_lut.blockSignals(False)

        self.ui.slider_lut_lower.blockSignals(True)
        self.ui.slider_lut_lower.setValue(min(self.ui.slider_lut_upper.value(), self.ui.slider_lut_lower.value()))
        self.ui.slider_lut_lower.blockSignals(False)

        self.update_current_lut()
        self.update_lut_panel_silently()
        self.signal_update_image_view.emit()

    def slot_lut_panel_changed (self):
        self.update_current_lut()
        self.update_lut_panel_silently()
        self.signal_update_image_view.emit()

    def slot_reset_current_lut_range (self):
        self.signal_reset_current_lut_range.emit()

    def current_channel (self):
        return self.ui.combo_channel.currentIndex()

    def color_always (self):
        return self.ui.check_color_always.isChecked()

    def is_composite (self):
        return self.ui.check_composite.isChecked()
    
    def is_auto_lut (self):
        return self.ui.check_auto_lut.isChecked()


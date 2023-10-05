from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
import os
import processing.organizer as organizer


class WidgetOrganize(WidgetCommon):

	def build_middle_widget(self):
		middle_widget = QGroupBox("Settings", self)
		middle_layout = QHBoxLayout()
		middle_layout.setAlignment(Qt.AlignTop)
		middle_widget.setLayout(middle_layout)
		label = QLabel("Threshold")
		middle_widget.setToolTip("""Luminosity difference threshold
If two consecutives images have a luminosity difference above this threshold, then they'll be separated into different sets.

Decrease if several sequences are incorrectly grouped into one set.
Increase if a single sequence is incorrectly splitted into several sets.""")
		middle_layout.addWidget(label)
		middle_widget.setMaximumWidth(300)

		self.threshold_slider = QSlider(Qt.Horizontal)
		self.threshold_slider.setMinimum(0)
		self.threshold_slider.setMaximum(100)
		self.threshold_slider.setValue(25)
		self.threshold_slider.setTickPosition(QSlider.TicksBelow)
		self.threshold_slider.setTickInterval(5)
		self.threshold_slider.valueChanged.connect(self.value_changed)

		self.threshol_val = QLabel("")
		self.threshol_val.setMinimumWidth(30)
		self.threshol_val.setAlignment(Qt.AlignRight)
		self.value_changed()
		
		middle_layout.addWidget(label)
		middle_layout.addWidget(self.threshold_slider)
		middle_layout.addWidget(self.threshol_val)
		return middle_widget
	
	@staticmethod
	def slider_val_to_threshold(val):
		return round(val/100.0, 2)
	
	def value_changed(self):
		val = self.threshold_slider.value()
		self.threshol_val.setText("{}%".format(val))

	def __init__(self):
		super(WidgetOrganize, self).__init__("Organize", self.do_it, self.build_middle_widget)

	def do_it(self):
		self.job_start()
		
		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		threshold = WidgetOrganize.slider_val_to_threshold(self.threshold_slider.value())
		print("threshold {}".format(threshold))
		organizer.separate_hdr_sets(in_folder, out_folder, threshold, self.update)
		
		self.job_done()

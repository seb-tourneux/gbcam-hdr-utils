from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
import os
import processing.organizer as organizer


class WidgetOrganize(WidgetCommon):

	def build_middle_widget(self):
		middle_widget = QGroupBox("Settings", self)

		middle_layout = QVBoxLayout()
		middle_widget.setLayout(middle_layout)
		middle_widget.setMaximumWidth(300)

		self.threshold_widget = SliderLabeled(middle_widget, 0.25)
		self.threshold_widget.label.setText("Threshold")
		self.threshold_widget.setToolTip("""Luminosity difference threshold
If two consecutives images have a luminosity difference above this threshold, then they'll be separated into different sets.

Decrease if several sequences are incorrectly grouped into one set.
Increase if a single sequence is incorrectly splitted into several sets.""")

		max_nb_layout = QHBoxLayout()
		max_nb_layout.setAlignment(Qt.AlignTop)
		max_nb_widget = QWidget(middle_widget)
		max_nb_widget.setLayout(max_nb_layout)
		
		self.combo_split_mode = QComboBox()
		self.combo_split_mode.addItems(organizer.Mode._member_names_)
		
		max_nb_layout.addWidget(self.combo_split_mode)
		self.spin_box_max_nb = QSpinBox(minimum=1, maximum=100000000, value = 29, suffix=' images')
		max_nb_layout.addWidget(QLabel(" sets bigger than"))
		max_nb_widget.setToolTip("""How to handle sets that are strictly bigger than this value.

Split: can be used if several AEB sequences are not recognized as different.
Skip: can be usefull to filter out some video sets mixed with AEB sets.
Keep: keep the big set as is.""")
		max_nb_layout.addWidget(self.spin_box_max_nb)
		
		middle_layout.addWidget(self.threshold_widget)
		middle_layout.addWidget(max_nb_widget)
		
		return middle_widget



	def __init__(self):
		super(WidgetOrganize, self).__init__("Organize", self.do_it, self.build_middle_widget)

	def do_it(self):
		self.job_start()

		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		threshold = self.threshold_widget.get_value()
		max_nb_per_set = self.spin_box_max_nb.value()
		mode = organizer.Mode(self.combo_split_mode.currentIndex()+1)

		organizer.separate_hdr_sets(in_folder, out_folder, threshold, max_nb_per_set, mode, self.update)
		
		self.job_done()

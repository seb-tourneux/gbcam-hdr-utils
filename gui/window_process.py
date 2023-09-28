from .window_common import *
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QWidget, QSpinBox, QGroupBox
from .in_out_folders_selector import *


class WidgetProcess(WidgetCommon):
	def build_blend_widget(self):
		blend_widget = QGroupBox("Blend", self)
		blend_layout = QVBoxLayout()
		blend_layout.setAlignment(Qt.AlignTop)
		blend_widget.setLayout(blend_layout)
		self.checkbox_blend_average = QCheckBox("Average", self)
		blend_layout.addWidget(self.checkbox_blend_average)
		return blend_widget

	def build_gif_widget(self):
		gif_widget = QGroupBox("GIF", self)
		gif_layout = QVBoxLayout()
		gif_layout.setAlignment(Qt.AlignTop)
		gif_widget.setLayout(gif_layout)

		self.checkbox_gif_first_to_last = QCheckBox("First to last", self)
		self.checkbox_gif_last_to_first = QCheckBox("Last to first", self)
		self.checkbox_gif_depth = QCheckBox("Increasing depth", self)
		gif_layout.addWidget(self.checkbox_gif_first_to_last)
		gif_layout.addWidget(self.checkbox_gif_last_to_first)
		gif_layout.addWidget(self.checkbox_gif_depth)

		duration_layout = QVBoxLayout()
		duration_layout.setAlignment(Qt.AlignTop)
		duration_widget = QWidget(self)
		duration_widget.setLayout(duration_layout)

		self.spin_box_frame_duration = QSpinBox(minimum=1, maximum=10000, value = 100, suffix=' ms')
		duration_layout.addWidget(QLabel("Frame duration"))
		duration_layout.addWidget(self.spin_box_frame_duration)
		gif_layout.addWidget(duration_widget)
		return gif_widget

	def build_post_process_widget(self):
		post_widget = QGroupBox("Post-process", self)
		post_layout = QVBoxLayout()
		post_layout.setAlignment(Qt.AlignTop)
		post_widget.setLayout(post_layout)


		scale_factor_layout = QVBoxLayout()
		scale_factor_layout.setAlignment(Qt.AlignTop)
		scale_factor_widget = QWidget(self)
		scale_factor_widget.setLayout(scale_factor_layout)
		self.spin_box_scale_factor = QSpinBox(minimum=1, maximum=100, value = 10, suffix='x')
		scale_factor_layout.addWidget(QLabel("Scale"))
		scale_factor_layout.addWidget(self.spin_box_scale_factor)

		add_border_layout = QVBoxLayout()
		self.checkbox_add_border = QGroupBox("Add border", self)
		self.checkbox_add_border.setCheckable(True)
		self.checkbox_add_border.setChecked(False)

		# todo file selector, not folder
		self.border_file_selector = FolderSelectorLineWidget()
		add_border_layout.addWidget(self.border_file_selector)
		self.checkbox_add_border.setLayout(add_border_layout)

		post_layout.addWidget(self.checkbox_add_border)
		post_layout.addWidget(scale_factor_widget)

		return post_widget


	def build_middle_widget(self):
		middle_widget = QGroupBox("Settings", self)
		middle_layout = QHBoxLayout()
		middle_layout.setAlignment(Qt.AlignTop)
		middle_widget.setLayout(middle_layout)

		middle_layout.addWidget(self.build_blend_widget(), stretch=1)
		middle_layout.addWidget(self.build_gif_widget(), stretch=1)
		middle_layout.addWidget(self.build_post_process_widget(), stretch=1)
		return middle_widget

	def __init__(self):
		super(WidgetProcess, self).__init__("Process", self.do_it, self.build_middle_widget)

	def do_it(self):
		gif_first_to_last = self.checkbox_gif_first_to_last.isChecked()
		gif_last_to_first = self.checkbox_gif_last_to_first.isChecked()
		gif_depth = self.checkbox_gif_depth.isChecked()
		blend_average = self.checkbox_blend_average.isChecked()
		frame_duration = self.spin_box_frame_duration.value()

		print("todo")

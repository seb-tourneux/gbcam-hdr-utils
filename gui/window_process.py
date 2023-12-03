from .window_common import *
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QWidget, QSpinBox, QGroupBox, QLineEdit
from .in_out_folders_selector import *
import processing.process_batch as process_batch


class WidgetProcess(WidgetCommon):
	def build_blend_widget(self):
		blend_widget = QGroupBox("Blend", self)
		blend_layout = QVBoxLayout()
		blend_layout.setAlignment(Qt.AlignTop)
		blend_widget.setLayout(blend_layout)
		self.checkbox_blend_average = QCheckBox("Average", self)
		self.checkbox_blend_average.setChecked(True)
		blend_layout.addWidget(self.checkbox_blend_average)
		return blend_widget

	def build_gif_widget(self):
		gif_widget = QGroupBox("GIF", self)
		gif_layout = QVBoxLayout()
		gif_layout.setAlignment(Qt.AlignTop)
		gif_widget.setLayout(gif_layout)

		self.checkbox_gif_first_to_last = QCheckBox("Picture by picture", self)
		self.checkbox_gif_last_to_first = QCheckBox("Picture by picture (reverse)", self)
		self.checkbox_gif_depth = QCheckBox("Increasing depth", self)
		self.checkbox_gif_depth_reverse = QCheckBox("Increasing depth (reverse)", self)
		gif_layout.addWidget(self.checkbox_gif_first_to_last)
		gif_layout.addWidget(self.checkbox_gif_last_to_first)
		gif_layout.addWidget(self.checkbox_gif_depth)
		gif_layout.addWidget(self.checkbox_gif_depth_reverse)

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


		self.scale_factor_widget = QGroupBox("Scale", self)
		scale_factor_layout = QVBoxLayout()
		scale_factor_layout.setAlignment(Qt.AlignTop)
		self.scale_factor_widget.setLayout(scale_factor_layout)
		self.scale_factor_widget.setCheckable(True)
		self.scale_factor_widget.setChecked(False)
		self.spin_box_scale_factor = QSpinBox(minimum=1, maximum=100, value = 10, suffix='x')
		scale_factor_layout.addWidget(self.spin_box_scale_factor)

		add_border_layout = QVBoxLayout()
		self.checkbox_add_border = QGroupBox("Add border", self)
		self.checkbox_add_border.setCheckable(True)
		self.checkbox_add_border.setChecked(False)

		# todo file selector, not folder
		self.border_file_selector = FolderSelectorLineWidget(True)
		add_border_layout.addWidget(self.border_file_selector)
		self.checkbox_add_border.setLayout(add_border_layout)
		
		# PALETTE
		self.palette_group_widget = QGroupBox("Apply palette", self)
		self.palette_group_widget.setCheckable(True)
		self.palette_group_widget.setChecked(False)
		palette_group_layout = QVBoxLayout()
		palette_group_layout.setAlignment(Qt.AlignTop)
		self.palette_group_widget.setLayout(palette_group_layout)
		self.palette_text = QLineEdit()
		self.palette_text.setPlaceholderText("#000000 #555555 #aaaaaa #ffffff")
		palette_group_layout.addWidget(self.palette_text)

		post_layout.addWidget(self.checkbox_add_border)
		post_layout.addWidget(self.scale_factor_widget)
		post_layout.addWidget(self.palette_group_widget)

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

	@staticmethod
	def has_work_to_do(options):
		return any([
			options['gif_ascend'],
			options['gif_descend'],
			options['gif_depth'],
			options['gif_depth_reverse'],
			options['blend_average'],
			options['border_path'] != None,
			options['scale_factor'] != 1])
	
	def get_color_palette(self):
		if self.palette_group_widget.isChecked():
			#return ("#01162c", "#0460bf", "#7cbde8", "#fff7e1")
			return self.palette_text.text()
		else:
			return None

	def do_it(self):
		self.job_start()

		if not self.check_folders():
			return

		scale_factor = self.spin_box_scale_factor.value() if self.scale_factor_widget.isChecked() else 1
		border_path = self.border_file_selector.get_folder() if self.checkbox_add_border.isChecked() else None # todo get file
		options = {'gif_ascend' : self.checkbox_gif_first_to_last.isChecked(),
			    'gif_descend' : self.checkbox_gif_last_to_first.isChecked(),
				'gif_depth' : self.checkbox_gif_depth.isChecked(),
				'gif_depth_reverse' : self.checkbox_gif_depth_reverse.isChecked(),
				'blend_average' : self.checkbox_blend_average.isChecked(),
				'gif_frame_duration' : self.spin_box_frame_duration.value(),
				'scale_factor' : scale_factor,
				'border_path' : border_path,
				'color_palette' : self.get_color_palette()
			 }

		# todo : check palette
		#if not WidgetProcess.has_work_to_do(options):
		#	self.add_text("Nothing to do")

		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		process_batch.process_batch(in_folder, out_folder, options, self.update)

		self.job_done()

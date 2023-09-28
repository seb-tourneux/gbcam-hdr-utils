from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem

from .in_out_folders_selector import *
from .output_console import *
import processing.organizer as organizer
import os
from datetime import datetime

class WidgetCommon(QWidget):
	def __init__(self, stage_name, button_callback, build_middle_widget=None):
		super(WidgetCommon, self).__init__()

		self.stage_name = stage_name
		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.main_layout.setAlignment(Qt.AlignTop)

		self.folders_selector_widget = InOutFoldersSelectorWidget()
		self.main_layout.addWidget(self.folders_selector_widget)

		if build_middle_widget:

			self.middle_widget = build_middle_widget()
		else:
			self.middle_widget = QWidget(self)
		#print(self.middle_widget)
		self.main_layout.addWidget(self.middle_widget)

		self.main_layout.addStretch()

		do_it_btn = QPushButton(stage_name)
		do_it_btn.setMinimumHeight(50)
		self.main_layout.addWidget(do_it_btn)
		do_it_btn.clicked.connect(button_callback)

		self.output_console = OutputConsoleWidget()
		self.main_layout.addWidget(self.output_console)

	def check_folders(self):
		ok = True
		self.output_console.clear()
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()

		if (not in_folder) or (not os.path.isdir(in_folder)):
			self.add_text("Input folder does not exist: \"{}\"".format(in_folder))
			ok = False
		if (not out_folder) or (not os.path.isdir(out_folder)):
			self.add_text("Output folder does not exist: \"{}\"".format(out_folder))
			ok = False
		return ok

	def add_text(self, text):
		time = datetime.now().strftime("%H:%M:%S")
		self.output_console.add_text("[{}][{}] {}".format(time, self.stage_name, text))

	def job_done(self):
		self.add_text("Done")
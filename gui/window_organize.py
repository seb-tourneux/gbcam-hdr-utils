from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem

from gui.in_out_folders_selector import *
from gui.output_console import *
import processing.organizer as organizer
import os

class WidgetOrganize(QWidget):
	def __init__(self):
		super(WidgetOrganize, self).__init__()

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.main_layout.setAlignment(Qt.AlignTop)
		
		self.folders_selector_widget = InOutFoldersSelectorWidget()
		self.main_layout.addWidget(self.folders_selector_widget)
		
		convert_btn = QPushButton("Organize")
		convert_btn.setMinimumHeight(50)
		self.main_layout.addWidget(convert_btn)
		convert_btn.clicked.connect(self.organize)
		
		self.main_layout.addStretch()
		
		self.output_console = OutputConsoleWidget()
		self.main_layout.addWidget(self.output_console)

	def organize(self):
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		
		self.output_console.clear()
		if (in_folder and os.path.isdir(in_folder) and
			out_folder and os.path.isdir(out_folder)):
			organizer.separate_hdr_sets(in_folder, out_folder, self.output_console.add_text)
		else:
			if not os.path.isdir(in_folder):
				self.output_console.add_text("Input folder does not exist: \"{}\"".format(in_folder))
			if not os.path.isdir(out_folder):
				self.output_console.add_text("Output folder does not exist: \"{}\"".format(out_folder))


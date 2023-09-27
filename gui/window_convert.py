from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem

from gui.in_out_folders_selector import *
from gui.output_console import *
import processing.parser as parser
import os

class WidgetConvert(QWidget):
	def __init__(self):
		super(WidgetConvert, self).__init__()

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.main_layout.setAlignment(Qt.AlignTop)
		
		self.folders_selector_widget = InOutFoldersSelectorWidget()
		self.main_layout.addWidget(self.folders_selector_widget)
		
		convert_btn = QPushButton("Convert")
		convert_btn.setMinimumHeight(50)
		self.main_layout.addWidget(convert_btn)
		convert_btn.clicked.connect(self.convert)
		
		self.main_layout.addStretch()
		
		self.output_console = OutputConsoleWidget()
		self.main_layout.addWidget(self.output_console)

	def convert(self):
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		
		self.output_console.clear()
		if os.path.isdir(in_folder):
			parser.convert_folder(in_folder, out_folder, self.output_console.add_text)
		else:
			self.output_console.set_text("Input folder does not exist: \"{}\"".format(in_folder))
			

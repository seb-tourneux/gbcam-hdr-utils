from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem

from .in_out_folders_selector import *
from .output_console import *
import processing.organizer as organizer
import os

class WidgetCommon(QWidget):
	def __init__(self, button_name, button_callback, middle_layout=None):
		super(WidgetCommon, self).__init__()

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.main_layout.setAlignment(Qt.AlignTop)

		self.folders_selector_widget = InOutFoldersSelectorWidget()
		self.main_layout.addWidget(self.folders_selector_widget)

		self.main_layout.addStretch()

		self.middle_widget = QWidget(self)
		if middle_layout:
			self.middle_widget.setLayout(middle_layout())

		self.main_layout.addWidget(self.middle_widget)

		self.main_layout.addStretch()

		do_it_btn = QPushButton(button_name)
		do_it_btn.setMinimumHeight(50)
		self.main_layout.addWidget(do_it_btn)
		do_it_btn.clicked.connect(button_callback)

		self.output_console = OutputConsoleWidget()
		self.main_layout.addWidget(self.output_console)

from PySide6.QtWidgets import *
from PySide6.QtCore import *

from .window_common import *


class WidgetStitch(WidgetCommon):
	def build_middle_widget(self):
		images_widget = QWidget()
		images_layout = QHBoxLayout()
		images_widget.setLayout(images_layout)

		images_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                                 QSizePolicy.Expanding))

		match_widget = QGroupBox("Match", self)
		match_layout = QVBoxLayout()
		match_widget.setLayout(match_layout)
		match_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
		self.match_img_label = QLabel("test match")
		self.match_img_label.setStyleSheet("background-color: lightgreen") 
		self.match_img_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                                 QSizePolicy.Expanding))
		#self.match_img_label.setPixmap(myQPixmap) #todo

		match_buttons_widget = QWidget()
		match_buttons_layout = QHBoxLayout()
		match_buttons_widget.setLayout(match_buttons_layout)

		match_decline_button = QPushButton("Decline")
		match_accept_button = QPushButton("Accept")
		match_decline_button.clicked.connect(self.decline_match)
		match_accept_button.clicked.connect(self.accept_match)

		match_buttons_layout.addWidget(match_decline_button)
		match_buttons_layout.addWidget(match_accept_button)
		# todo shortcuts

		match_layout.addWidget(self.match_img_label)
		match_layout.addWidget(match_buttons_widget)

		match_buttons_layout.addWidget(match_decline_button)
		match_buttons_layout.addWidget(match_accept_button)

		# RESULT
		result_widget = QGroupBox("Result", self)
		result_layout = QVBoxLayout()
		result_widget.setLayout(result_layout)
		self.result_img_label = QLabel("test res")
		#self.match_img_label.setPixmap(myQPixmap) #todo
		result_layout.addWidget(self.result_img_label)

		images_layout.addWidget(match_widget)
		images_layout.addWidget(result_widget)
		return images_widget

	def __init__(self):
		super(WidgetStitch, self).__init__("Stitch", None, self.build_middle_widget, False)

	def accept_match(self):
		self.update("accept_match")
		# todo


	def decline_match(self):
		self.update("decline_match")
		#todo


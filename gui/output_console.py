from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui
from PySide6.QtGui import *
from PySide6.QtCore import *

class OutputConsoleWidget(QScrollArea):

	
	def __init__(self):
		super(OutputConsoleWidget, self).__init__()

		self.setWidgetResizable(True)
		content = QWidget(self)
		self.setWidget(content)
		lay = QVBoxLayout(content)

		self.label = QLabel(content)
		self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.label.setWordWrap(True)
		lay.addWidget(self.label)
		
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

	def set_text(self, text):
		self.label.setText(text)

	def add_text(self, text):
		prev_text = self.label.text()
		if prev_text != "":
			text = text + "\n" + prev_text
		self.set_text(text)
		
	def clear(self):
		self.set_text("")
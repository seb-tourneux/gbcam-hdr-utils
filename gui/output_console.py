from PySide6.QtWidgets import QWidget, QScrollArea, QLabel

class OutputConsoleWidget(QScrollArea):
	def __init__(self):
		super(OutputConsoleWidget, self).__init__()
		
	
		self.output_widget = QLabel("")
		#output_widget.setLayout(output_layout)
		self.setWidget(self.output_widget)
		self.setMinimumHeight(100)
	
	def set_text(self, text):
		# bug with scroll area not updating ? need to recreate widget
		self.output_widget = QLabel(text)
		self.setWidget(self.output_widget)
		vbar = self.verticalScrollBar()
		vbar.setValue(vbar.maximum())
		
	def add_text(self, text):
		prev_text = self.output_widget.text()
		if prev_text != "":
			prev_text += "\n"
		self.set_text(prev_text + text)
		
	def clear(self):
		self.set_text("")
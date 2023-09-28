from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
import os

class WidgetOrganize(WidgetCommon):
	def build_middle_widget(self):
		middle_layout = QGridLayout()
		self.middle_label = QLabel("test")
		middle_layout.addWidget(self.middle_label)
		return middle_layout

	def __init__(self):
		super(WidgetOrganize, self).__init__("Organize", self.do_it, self.build_middle_widget)

	def do_it(self):
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


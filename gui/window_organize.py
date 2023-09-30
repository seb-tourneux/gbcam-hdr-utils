from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
import os

class WidgetOrganize(WidgetCommon):


	def __init__(self):
		super(WidgetOrganize, self).__init__("Organize", self.do_it)

	def do_it(self):
		self.job_start()
		
		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		organizer.separate_hdr_sets(in_folder, out_folder, self.update)
		
		self.job_done()

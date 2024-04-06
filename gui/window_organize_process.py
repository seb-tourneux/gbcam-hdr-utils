from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
from .window_organize import *
from .window_process import *
import os
import processing.organizer as organizer
import shutil

class WidgetOrganizeProcess(WidgetCommon):

	def build_middle_widget(self):
		
		middle_widget = QWidget()
		middle_layout = QVBoxLayout()
		middle_widget.setLayout(middle_layout)

		self.wOrg = WidgetOrganize()
		self.wProc = WidgetProcess()
		self.middle_widget_organize = self.wOrg.build_middle_widget()
		self.middle_widget_organize.setTitle("Organize Settings")
		self.middle_widget_process = self.wProc.build_middle_widget()
		self.middle_widget_process.setTitle("Process Settings")
		
		self.checkbox_keep_intermediate = QCheckBox("Keep intermediate Organize folder", self)


		middle_layout.addWidget(self.middle_widget_organize)
		middle_layout.addWidget(self.middle_widget_process)
		middle_layout.addWidget(self.checkbox_keep_intermediate)


		return middle_widget

	def do_it(self):
		self.job_start()

		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		
		temp_org_folder = os.path.join(out_folder, "AEB_organized")
		self.wOrg.do_it_org(in_folder, temp_org_folder)
		
		
		self.wProc.do_it_proc(temp_org_folder, out_folder)
		
		if not self.checkbox_keep_intermediate.isChecked():
			shutil.rmtree(temp_org_folder)
		
		self.job_done()

	def __init__(self):
		super(WidgetOrganizeProcess, self).__init__("Organize+Process", self.do_it, self.build_middle_widget)

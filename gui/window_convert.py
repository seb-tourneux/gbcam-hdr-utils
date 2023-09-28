from .window_common import *


class WidgetConvert(WidgetCommon):
	def __init__(self):
		super(WidgetConvert, self).__init__("Convert", self.do_it)

	def do_it(self):
		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		parser.convert_folder(in_folder, out_folder, self.add_text)

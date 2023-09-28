from .window_common import *


class WidgetConvert(WidgetCommon):
	def __init__(self):
		super(WidgetConvert, self).__init__("Convert", self.do_it)

	def do_it(self):
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		
		self.output_console.clear()
		if os.path.isdir(in_folder):
			parser.convert_folder(in_folder, out_folder, self.output_console.add_text)
		else:
			self.output_console.set_text("Input folder does not exist: \"{}\"".format(in_folder))
			

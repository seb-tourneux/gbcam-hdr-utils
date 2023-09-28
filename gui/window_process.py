from .window_common import *

class WidgetProcess(WidgetCommon):
	def __init__(self):
		super(WidgetProcess, self).__init__("Process", self.do_it)

	def do_it(self):
		print("todo")
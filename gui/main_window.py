import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget, QTabWidget

from .window_convert import *
from .window_organize import *
from .window_process import *
from .window_stitch import *
import processing.infos as infos


class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle(infos.get_software_name())

		self.main_layout = QHBoxLayout()
		self.main_widget = QWidget()
		self.main_widget.setLayout(self.main_layout)

		tabwidget = QTabWidget()
		tabwidget.addTab(WidgetConvert(), "Convert")
		tabwidget.addTab(WidgetOrganize(), "Organize")
		tabwidget.addTab(WidgetProcess(), "Process")
		tabwidget.addTab(WidgetStitch(), "Stitch")
		
		tabwidget.setTabToolTip(0, "Convert .sav files to .png")
		tabwidget.setTabToolTip(1, "Organize AEB sequences into separate folders")
		tabwidget.setTabToolTip(2, "Process pictures sets : average, create gifs. Processing is done subfolder by subfolder")
		tabwidget.setTabToolTip(3, "Stitch pictures from a folder")
		
		self.main_layout.addWidget(tabwidget)
		
		self.setCentralWidget(self.main_widget)


def launch():
	if not QApplication.instance():
		app = QApplication(sys.argv)
	else:
		app = QApplication.instance()

	window = MainWindow()
	window.update()
	window.show()
	window.resize(1200, 800)
	sys.exit(app.exec())
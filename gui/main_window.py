import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget, QTabWidget

from gui.window_convert import *



class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle("gbcam-hdr-utils")

		self.main_layout = QHBoxLayout()
		self.main_widget = QWidget()
		self.main_widget.setLayout(self.main_layout)

		tabwidget = QTabWidget()
		tabwidget.addTab(WidgetConvert(), "Convert")
		tabwidget.addTab(QLabel("TODO WidgetOrganize()"), "Organize")
		tabwidget.addTab(QLabel("TODO WidgetBlend()"), "Blend")
		tabwidget.addTab(QLabel("TODO WidgetStitch()"), "Stitch")
		
		tabwidget.setTabToolTip(0, "Convert .sav files to .png")
		tabwidget.setTabToolTip(1, "Organize AEB sequences into separate folders")
		tabwidget.setTabToolTip(2, "Blend pictures subfolder by subfolder")
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
	window.resize(1200, 500)
	sys.exit(app.exec())
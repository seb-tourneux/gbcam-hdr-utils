import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget, QTabWidget

from .window_convert import *
from .window_organize import *
from .window_process import *
from .window_organize_process import *
from .window_making_of import *
#from .window_stitch import *
from .window_stitch_fourier import *
from .window_auto import *
import processing.infos as infos


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle(infos.get_software_name())

        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)


        step_tabwidget = QTabWidget()
        step_tabwidget.addTab(WidgetConvert(), "Convert")
        step_tabwidget.addTab(WidgetOrganize(), "Organize")
        step_tabwidget.addTab(WidgetProcess(), "Process")
        #step_tabwidget.addTab(WidgetOrganizeProcess(), "Organize+Process")
        step_tabwidget.addTab(WidgetStitchFourier(), "Stitch")
        step_tabwidget.addTab(WidgetMakingOf(), "Making-Of")
        
        step_tabwidget.setTabToolTip(0, "Convert .sav files to .png")
        step_tabwidget.setTabToolTip(1, "Organize AEB sequences into separate folders")
        step_tabwidget.setTabToolTip(2, "Process pictures sets : average, create gifs. Processing is done subfolder by subfolder")
        step_tabwidget.setTabToolTip(3, "Equivalent to \"Organize\" then \"Process\"")
        step_tabwidget.setTabToolTip(4, "Stitch pictures from a folder")
        
        main_tab_widget = QTabWidget()
        main_tab_widget.addTab(WidgetAuto(), "Auto")
        main_tab_widget.addTab(step_tabwidget, "Step by step")
        main_tab_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
 
  
        self.main_layout.addWidget(main_tab_widget)

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
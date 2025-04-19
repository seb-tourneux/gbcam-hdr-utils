from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
from .window_organize import *
from .window_process import *
from .window_stitch_fourier import *
from .window_making_of import *
import os
import processing.auto as auto
import shutil

class WidgetAuto(WidgetCommon):

    def build_middle_widget(self):
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(scroll_widget)



        self.wOrg = WidgetOrganize()
        self.wProc = WidgetProcess()
        self.wStitch = WidgetStitchFourier()
        self.wMakingOf = WidgetMakingOf()

        self.making_of_group = FoldableGroup("Making-Of")
        self.stitch_group = FoldableGroup("Stitch", self.making_of_group)
        self.proc_group = FoldableGroup("Process", self.stitch_group)
        self.org_group = FoldableGroup("Organize", self.proc_group)

        # Add your existing widgets to the groups
        self.org_group.addWidget(self.wOrg.build_middle_widget())
        self.proc_group.addWidget(self.wProc.build_middle_widget())
        self.stitch_group.addWidget(self.wStitch.build_middle_widget())
        self.making_of_group.addWidget(self.wMakingOf.build_middle_widget())

        # Add groups to the main layout
        scroll_layout.addWidget(self.org_group)
        scroll_layout.addWidget(self.proc_group)
        scroll_layout.addWidget(self.stitch_group)
        scroll_layout.addWidget(self.making_of_group)
        scroll_layout.addStretch()

        scroll.viewport().setAutoFillBackground(False)
        scroll_widget.setAutoFillBackground(False)
        
        return scroll

    def do_it(self):
        self.job_start()

        if not self.check_folders():
            return
        
        (in_folder, out_folder) = self.folders_selector_widget.get_folders()
        
        options_org = None
        options_proc = None
        options_stitch = None
        options_making_of = None
        if self.org_group.isEnabled():
            options_org = self.wOrg.get_options()
        if self.proc_group.isEnabled():
            options_proc = self.wProc.get_options()
        if self.stitch_group.isEnabled():
            options_stitch = self.wStitch.get_options()
        if self.making_of_group.isEnabled():
            options_making_of = self.wMakingOf.get_options()
        
        auto.auto_process(in_folder, out_folder, options_org, options_proc, options_stitch, options_making_of, self.update)
        self.job_done()

    def __init__(self):
        super(WidgetAuto, self).__init__("Auto", self.do_it, self.build_middle_widget, False)

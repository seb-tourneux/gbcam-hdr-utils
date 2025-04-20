from PySide6.QtWidgets import QLabel

from .window_common import *
import os
import processing.align_fourier as align_fourier


class WidgetStitchFourier(WidgetCommon):

    def build_middle_widget(self):
        middle_widget = QWidget()
        middle_layout = QVBoxLayout()
        middle_widget.setLayout(middle_layout)

        label = QLabel("Stitch pictures, no settings")
        middle_layout.addWidget(label)

        return middle_widget

    def __init__(self):
        super(WidgetStitchFourier, self).__init__("Stitch", self.do_it, self.build_middle_widget)

    def do_it_stitch(self, in_folder, out_folder):
        align_fourier.auto_align(in_folder, out_folder, self.update)

    def get_options(self):
        return align_fourier.default_options()

    def do_it(self):
        self.job_start()

        if not self.check_folders():
            return
        
        (in_folder, out_folder) = self.folders_selector_widget.get_folders()
        self.do_it_stitch(in_folder, out_folder)
        
        self.job_done()

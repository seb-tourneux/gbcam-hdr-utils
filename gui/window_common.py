from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem, QProgressBar, QGroupBox, QCheckBox
from PySide6.QtCore import *

from .in_out_folders_selector import *
from .output_console import *
import processing.organizer as organizer
import os
from datetime import datetime


class SliderLabeled(QWidget):
    def __init__(self, parent, default_value):
        super(SliderLabeled, self).__init__(parent)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        self.label = QLabel()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100*default_value)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.value_changed)

        self.val_label = QLabel("")
        self.val_label.setMinimumWidth(30)
        self.val_label.setAlignment(Qt.AlignRight)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.val_label)

        self.value_changed()

    def value_changed(self):
        val = self.slider.value()
        self.val_label.setText("{}%".format(val))

    @staticmethod
    def slider_val_to_threshold(val):
        return round(val/100.0, 2)

    def get_value(self):
        return SliderLabeled.slider_val_to_threshold(self.slider.value())

class WidgetCommon(QWidget):
    def __init__(self, stage_name, button_callback, build_middle_widget=None, stretch = True):
        super(WidgetCommon, self).__init__()

        self.stage_name = stage_name
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.folders_selector_widget = InOutFoldersSelectorWidget()
        self.main_layout.addWidget(self.folders_selector_widget)

        if build_middle_widget:
            self.middle_widget = build_middle_widget()
        else:
            self.middle_widget = QWidget(self)
        if self.middle_widget:
            self.main_layout.addWidget(self.middle_widget)

        if stretch:
            self.main_layout.addStretch()

        self.pbar = QProgressBar(self)
        self.pbar.setValue(0)
        self.pbar.setAlignment(Qt.AlignCenter);
        self.main_layout.addWidget(self.pbar)

        if button_callback:
            do_it_btn = QPushButton(stage_name)
            do_it_btn.setMinimumHeight(50)
            self.main_layout.addWidget(do_it_btn)
            do_it_btn.clicked.connect(button_callback)
            
        self.output_console = OutputConsoleWidget()
        self.main_layout.addWidget(self.output_console)

        self.folders_selector_widget.signal_in_folder_selected().connect(self.update_in_folder_selected)


    def check_folders(self):
        ok = True
        self.output_console.clear()
        (in_folder, out_folder) = self.folders_selector_widget.get_folders()

        if (not in_folder) or (not os.path.isdir(in_folder)):
            self.update("Input folder does not exist: \"{}\"".format(in_folder))
            ok = False
        if (not out_folder) or (not os.path.isdir(out_folder)):
            self.update("Output folder does not exist: \"{}\"".format(out_folder))
            ok = False
        return ok

    def update(self, text, completion = None):
        
        completion_text = ""
        if not completion is None:
            self.pbar.setValue(100*completion)
            completion_text = "{:.2f}%".format(100*completion).rjust(8)
            completion_text = "[{}]".format(completion_text)

        if text:
            time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.output_console.add_text("[{}][{}]{} {}".format(time, self.stage_name, completion_text, text))

    def job_start(self):
        self.output_console.clear()
        self.update("", 0.0)
        
    def job_done(self):
        self.update("Done", 1.0)

    def update_in_folder_selected(self):
        self.output_console.clear()
        self.update(None, 0.0)


class FoldableGroup(QWidget):
    def __init__(self, title: str, bottom_widget : QWidget = None, parent=None):
        super().__init__(parent)
        self.setProperty("name", f"FoldableGroup_{title}")
        self.bottom_widget = bottom_widget
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.group_box = QGroupBox(title)
        self.group_box.setCheckable(True)
        self.main_layout.addWidget(self.group_box)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.group_box.clicked.connect(self._on_checkbox_changed)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.content_widget.setLayout(self.content_layout)
        self.group_box_layout = QVBoxLayout()
        self.group_box_layout.setContentsMargins(0, 0, 0, 0)
        self.group_box.setLayout(self.group_box_layout)
        self.group_box_layout.addWidget(self.content_widget)
        
        self.setEnabled(True)
    
    def _on_checkbox_changed(self, enabled):
        self.setContentEnabled(enabled)

    def addWidget(self, widget):
        new_widget = QWidget()
        new_widget.setLayout(widget.layout())
        new_widget.setMaximumWidth(widget.maximumWidth())
        new_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.content_layout.addWidget(new_widget)
    
    def isEnabled(self) -> bool:
        """Check if the group is enabled"""
        return self.group_box.isChecked() and self.content_widget.isEnabled()
    
    def setContentEnabled(self, enabled: bool):
        self.content_widget.setEnabled(enabled)
        self.content_widget.setVisible(enabled)
        
        if self.bottom_widget:
            self.bottom_widget.setEnabled(enabled)
            self.bottom_widget.setContentEnabled(enabled)

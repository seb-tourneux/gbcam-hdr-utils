from PySide6.QtWidgets import QLabel, QGridLayout

from .window_common import *
import os
import processing.making_of as making_of

class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Picker")
        self.setGeometry(100, 100, 300, 200)

        self.button = QPushButton("", self)
        self.button.clicked.connect(self.open_color_picker)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.rgb = (255, 255, 255)
        self.set_button_color(self.rgb)

    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.rgb = (color.red(), color.green(), color.blue())
            self.set_button_color(self.rgb)

    def set_button_color(self, rgb):
        r, g, b = rgb
        self.button.setStyleSheet(f"""
            background-color: rgb({r},{g},{b});
            color: black;
            border: 1px solid black;  /* Black border */
            padding: 5px;  /* Adds spacing inside the button */
        """)


class WidgetMakingOf(WidgetCommon):

	def build_middle_widget(self):
		middle_widget = QGroupBox("Settings", self)

		middle_layout = QVBoxLayout()
		middle_widget.setLayout(middle_layout)
		middle_widget.setMaximumWidth(300)

		frame_duration_layout = QVBoxLayout()
		frame_duration_layout.setAlignment(Qt.AlignTop)
		frame_duration_widget = QWidget(self)
		frame_duration_widget.setLayout(frame_duration_layout)
		self.spin_box_frame_duration = QSpinBox(minimum=1, maximum=10000, value = 100, suffix=' ms')
		frame_duration_layout.addWidget(QLabel("Frame duration"))
		frame_duration_layout.addWidget(self.spin_box_frame_duration)
		middle_layout.addWidget(frame_duration_widget)

		fade_duration_layout = QVBoxLayout()
		fade_duration_layout.setAlignment(Qt.AlignTop)
		fade_duration_widget = QWidget(self)
		fade_duration_widget.setLayout(fade_duration_layout)
		self.spin_box_fade_duration = QSpinBox(minimum=0, maximum=10000, value = 1000, suffix=' ms')
		fade_duration_layout.addWidget(QLabel("Fade (clean image only)"))
		fade_duration_layout.addWidget(self.spin_box_fade_duration)
		middle_layout.addWidget(fade_duration_widget)

		freeze_duration_layout = QVBoxLayout()
		freeze_duration_layout.setAlignment(Qt.AlignTop)
		freeze_duration_widget = QWidget(self)
		freeze_duration_widget.setLayout(freeze_duration_layout)
		self.spin_box_freeze_duration = QSpinBox(minimum=0, maximum=10000, value = 3000, suffix=' ms')
		freeze_duration_layout.addWidget(QLabel("Hold last"))
		freeze_duration_layout.addWidget(self.spin_box_freeze_duration)
		middle_layout.addWidget(freeze_duration_widget)
	
		color_picker_layout = QVBoxLayout()
		color_picker_layout.setAlignment(Qt.AlignTop)
		color_picker_widget = QWidget(self)
		color_picker_widget.setLayout(color_picker_layout)
		self.color_picker = ColorPicker()
		color_picker_layout.addWidget(QLabel("Background color"))
		color_picker_layout.addWidget(self.color_picker)
		middle_layout.addWidget(color_picker_widget)
  	
		return middle_widget

	def __init__(self):
		super(WidgetMakingOf, self).__init__("Making-Of", self.do_it, self.build_middle_widget)

	def do_it_making_of(self, in_folder, out_folder):
		options = {'frame_duration' : self.spin_box_frame_duration.value(),
					'freeze_duration' : self.spin_box_freeze_duration.value(),
					'fade_duration' : self.spin_box_fade_duration.value(),
					'bg_color' : self.color_picker.rgb
				}

		making_of.make_gifs(in_folder, out_folder, self.update)
		making_of.make_gif_all(in_folder, out_folder, options, self.update)

	def do_it(self):
		self.job_start()

		if not self.check_folders():
			return
		
		(in_folder, out_folder) = self.folders_selector_widget.get_folders()
		self.do_it_making_of(in_folder, out_folder)
		
		self.job_done()

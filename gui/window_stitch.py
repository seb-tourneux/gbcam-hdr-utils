from PySide6.QtWidgets import *
from PySide6.QtCore import *

from .window_common import *
import processing.align as align
import processing.data as data

def cv2_to_pixmap(image):
	if image is None:
		return QtGui.QPixmap()
	else:
		image = image.copy(order='C')
		image = QtGui.QImage(image, image.shape[1],\
							  image.shape[0], image.shape[1] * 3,QtGui.QImage.Format_RGB888)
		return QtGui.QPixmap(image)

class WidgetStitch(WidgetCommon):
	
	def init_match(self, folder):
		self.result_img_label.setPixmap(QtGui.QPixmap())
		self.output_console.clear()
		
		self.nb_fails = [0]
		self.res_merged_img = None
		self.accepted_images_delta = []
		
		self.unmatched_images = align.load_folder_cv2(folder)
		if not self.unmatched_images:
			self.update("Cannot find images in folder {} images".format(folder))
		else:
			self.set_name = os.path.basename(folder)
			self.nb_images_total = len(self.unmatched_images)
			self.update("Loaded {} images".format(self.nb_images_total))
			
			self.match_decline_button.setEnabled(True)
			self.match_accept_button.setEnabled(True)
			self.set_button_accept_values(False)

			self.try_match()
		
	def try_match(self):
		(self.res_try_match, self.res_merged_img) = align.process_one_match(self.unmatched_images, self.res_merged_img, self.accepted_images_delta, self.nb_fails)
		(img_matches, img2, delta) = self.res_try_match
		self.match_img_label.setPixmap(cv2_to_pixmap(img_matches))

	def get_completion(self):
		return (self.nb_images_total-len(self.unmatched_images))/self.nb_images_total

	def accept_match(self):
		if self.match_accept_button.text() == "Save...":
			self.end()
		else:
			self.accept_decline_match(True)
	def decline_match(self):
		self.accept_decline_match(False)
	
	def accept_decline_match(self, accepted):
		
		self.res_merged_img = align.process_match_accept_decline(	self.unmatched_images, 
																   self.res_merged_img, 
																   self.accepted_images_delta, 
																   self.nb_fails, 
																   self.res_try_match[1], #img matched
																   self.res_try_match[2], #delta
																   accepted)	
		if accepted:
			self.result_img_label.setPixmap(cv2_to_pixmap(self.res_merged_img))
			self.update("Match accepted", self.get_completion())
		else:
			if self.nb_fails[0] > len(self.unmatched_images):
				self.update("Could not find match for {} images".format(len(self.unmatched_images)), 1.0)
				self.end()
			else:
				self.update("Match declined, will try later", self.get_completion())
			
		if len(self.unmatched_images) == 0:
			self.end()
		else:
			self.try_match()
	
	@staticmethod
	def folder_ok(folder):
		return (folder) and (folder != "") and (os.path.isdir(folder))
	
	def end(self):
		self.match_decline_button.setEnabled(False)
		self.match_accept_button.setEnabled(False)

		(_, out_folder) = self.folders_selector_widget.get_folders()
		if not WidgetStitch.folder_ok(out_folder):
			self.update("Select a save directory")
			out_folder = QFileDialog.getExistingDirectory(self, "Save Directory",
                                       "",
                                       QFileDialog.ShowDirsOnly)
		
		if WidgetStitch.folder_ok(out_folder):
			align.save_layers(self.accepted_images_delta, self.unmatched_images, out_folder, self.set_name)
			self.update("Saved in {}".format(out_folder), 1.0)
			self.folders_selector_widget.out_folder_selector.folder_selector_line.folder_line_edit.setText(out_folder)
		else:
			self.update("Invalid output folder")
			self.match_accept_button.setEnabled(True)
			self.set_button_accept_values(True)



	def update_in_folder_selected(self, folder):
		if folder and folder != "":
			self.init_match(folder)
		else:
			self.output_console.clear()

	def set_button_accept_values(self, save_mode):
		if save_mode:
			self.match_accept_button.setText("Save...")
			self.match_accept_button.setToolTip("Save result")
		else:
			self.match_accept_button.setText("Accept →")
			self.match_accept_button.setToolTip("Accept the proposed match\nShortcut: Right Arrow")

	def build_middle_widget(self):
		images_widget = QWidget()
		images_layout = QHBoxLayout()
		images_widget.setLayout(images_layout)


		match_widget = QGroupBox("Match", self)
		match_layout = QVBoxLayout()
		match_widget.setLayout(match_layout)
		match_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
		self.match_img_label = QLabel()
		#self.match_img_label.setStyleSheet("background-color: lightgreen") 

		self.match_img_label.setMinimumHeight(300)
		self.match_img_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
		
		#self.match_img_label.setPixmap(myQPixmap) #todo

		self.match_buttons_widget = QWidget()
		match_buttons_layout = QHBoxLayout()
		self.match_buttons_widget.setLayout(match_buttons_layout)

		self.match_decline_button = QPushButton("← Decline")
		self.match_decline_button.setToolTip("Decline the proposed match.\nThe picture will be tried again later, as it may match with next pictures added to the stitch.\nShortcut: Left Arrow")
		self.match_accept_button = QPushButton()
		self.set_button_accept_values(False)
		
		self.match_decline_button.clicked.connect(self.decline_match)
		self.match_accept_button.clicked.connect(self.accept_match)


		match_buttons_layout.addWidget(self.match_decline_button)
		match_buttons_layout.addWidget(self.match_accept_button)
		match_buttons_layout.setAlignment(Qt.AlignBottom)

		QShortcut(QtCore.Qt.Key_Right, self, self.accept_match)
		QShortcut(QtCore.Qt.Key_Left, self, self.decline_match)

		self.match_decline_button.setEnabled(False)
		self.match_accept_button.setEnabled(False)

		match_layout.addWidget(self.match_img_label)
		match_layout.addWidget(self.match_buttons_widget)

		# RESULT
		result_widget = QGroupBox("Result", self)
		result_layout = QVBoxLayout()
		result_widget.setLayout(result_layout)
		self.result_img_label = QLabel("")
		self.result_img_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)

		result_layout.addWidget(self.result_img_label)

		images_layout.addWidget(match_widget)
		images_layout.addWidget(result_widget)
		return images_widget


	def __init__(self):
		super(WidgetStitch, self).__init__("Stitch", None, self.build_middle_widget, False)

		self.folders_selector_widget.signal_in_folder_selected().connect(self.update_in_folder_selected)


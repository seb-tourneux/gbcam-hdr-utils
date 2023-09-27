import sys
from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSlider
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries
from PySide6.QtGui import QGradient, QPen, QLinearGradient, QPainter, QPalette, QImage, QPixmap


import data
import process


def image_info_text(image):
	return "mean {:.3f} min {:.3f} max {:.3f}".format(image.mean(), image.min(), image.max(),)

class ImageMask(QWidget):
	def __init__(self, image, mask, path):
		super(ImageMask, self).__init__()
		
		main_layout = QHBoxLayout()

		image_label = QLabel()
		image_mask_label = QLabel()
		image_label.setPixmap(QPixmap(data.array_to_ImageQt(image)))
		image_mask_label.setPixmap(QPixmap(data.array_to_ImageQt(mask)))
		image_label.setToolTip(path)
		
		main_layout.addWidget(image_label)
		main_layout.addWidget(image_mask_label)
		
		info_w = QWidget()
		infos = {
			"Image {}".format(image_info_text(image)),
			"Mask {}".format(image_info_text(mask))
			}
		info_layout = QVBoxLayout()
		for txt in infos:
			label = QLabel()
			label.setText(txt)
			info_layout.addWidget(label)
		info_w.setLayout(info_layout)
		main_layout.addWidget(info_w)


		self.setLayout(main_layout)




class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		# todo export settings
		self.lum_value = 0.0
		
		self.setWindowTitle("exposure-fusion-gui")
		#self.setBackgroundRole(QPalette.Dark)
		
		self.main_layout = QHBoxLayout()
		self.main_widget = QWidget()
		self.main_widget.setLayout(self.main_layout)
		
		# input image
		self.input_scroll_area = QScrollArea()	
		self.main_layout.addWidget(self.input_scroll_area)
		
		# result
		self.right_layout = QVBoxLayout()
		self.right_widget = QWidget()
		self.right_widget.setLayout(self.right_layout)
		self.image_res_widget = QWidget()
		
		self.methods = ["average", "mertens"]
		self.result_dict = {}
		res_images_layout = QVBoxLayout()

		for method in self.methods:
			img_label_layout = QVBoxLayout()

			print("label method {}".format(method))
			label_method = QLabel()
			label_method.setText(method)
			#label_method.setAttribute(Qt.WA_StyledBackground, True)
			#label_method.setStyleSheet('background-color: red;')

			img_label_layout.addWidget(label_method)

			image_label = QLabel()
			image_label.setToolTip(method)
			self.result_dict[method] = image_label
			
			img_label_layout.addWidget(image_label)
			

			
			img_label_widget = QWidget()
			img_label_widget.setLayout(img_label_layout)
			
			res_images_layout.addWidget(img_label_widget)


		self.image_res_widget.setLayout(res_images_layout)
		self.right_layout.addWidget(self.image_res_widget)
		
		self.lum_slider = QSlider(Qt.Horizontal, self)
		#self.lum_slider.setGeometry(10, 10, 300, 40)
		self.lum_slider.setMaximum(100)

		self.lum_slider.valueChanged.connect(self.lum_slider_value_changed)
		self.right_layout.addWidget(self.lum_slider)

		self.main_layout.addWidget(self.right_widget)
		self.setCentralWidget(self.main_widget)
	
	def lum_slider_value_changed(self, value):
		self.lum_value = value / 100.0
		self.update()
		
	def update(self):
		input_images_layout = QVBoxLayout()
		folder_path = "input\\olympus1a"
		
		# todo : store that (ie do not reload from disk every update)
		array_paths = data.get_arrays_and_path_from_folder(folder_path)
		images = list(zip(*array_paths))[0]
		
		masks = process.compute_masks(images, process.Method.CONTRAST, self.lum_value)
		for ((arr, path), mask) in zip(array_paths, masks):
			w = ImageMask(arr, mask, path)
			input_images_layout.addWidget(w)
		
		input_images_widget = QWidget()
		input_images_widget.setLayout(input_images_layout)
		self.input_scroll_area.setWidget(input_images_widget)



		print("Updating with lum {}".format(self.lum_value))
		
		
		fusion_arr = process.fusion(images, masks)
		#average_arr = process.average(images)
		#fusion_arr = (1-self.lum_value)*fusion_arr + self.lum_value*average_arr
		#average_arr = process.gammaCorrection(fusion_arr, self.lum_value)
		
		ratio = 3.0
		average_pixmap = QPixmap(data.array_to_ImageQt(fusion_arr)).scaledToWidth(ratio*fusion_arr.shape[1])
		self.result_dict["average"].setPixmap(average_pixmap)

		mertens_arr = process.merge_mertens(images, self.lum_value)
		mertens_pixmap = QPixmap(data.array_to_ImageQt(mertens_arr)).scaledToWidth(ratio*mertens_arr.shape[1])
		self.result_dict["mertens"].setPixmap(mertens_pixmap)


			


		

if __name__ == "__main__":
	if not QApplication.instance():
		app = QApplication(sys.argv)
	else:
		app = QApplication.instance()

	window = MainWindow()
	window.update()
	window.show()
	window.resize(1200, 500)
	sys.exit(app.exec())